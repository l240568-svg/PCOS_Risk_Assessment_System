
import datetime
from datetime import datetime, timezone
import secrets

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.auth.schemas import LoginRequest, RegisterRequest, OTPVerificationRequest
from app.auth.utils import create_access_token,create_refresh_token, hash_value, validate_password_strength, verify_hash, generate_OTP, otp_expiration_time, decode_token
from app.users.models import User
from app.auth.otp_service import create_otp_record, get_latest_valid_otp, mark_otp_as_used
from app.emails.email_service import send_otp_email
from app.auth.otp_service import OTPPurpose
from app.auth.models import OTPCode
from app.auth.models import RevokedToken, RefreshToken




def register_doctor(db: Session, doctor_data: RegisterRequest) -> User:
    existing_email = db.query(User).filter(User.email == doctor_data.email).first()

    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    existing_license = (
        db.query(User)
        .filter(User.license_number == doctor_data.license_number)
        .first()
    )

    if existing_license:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="License number already registered",
        )

    if doctor_data.specialization not in ["Gynecologist", "Endocrinologist"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid specialization",
        )
    
    try:
        validate_password_strength(doctor_data.password)
    except ValueError as error:
        raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=str(error),
    )

    new_doctor = User(
        first_name=doctor_data.first_name,
        last_name=doctor_data.last_name,
        email=doctor_data.email,
        specialization=doctor_data.specialization,
        hospital=doctor_data.hospital,
        clinic_address=doctor_data.clinic_address,
        license_number=doctor_data.license_number,
        password_hash=hash_value(doctor_data.password),
    )

    db.add(new_doctor)
    db.commit()
    db.refresh(new_doctor)

    return new_doctor


def login_doctor(
    db: Session,
    login_data: LoginRequest,
) -> tuple[str, str]:
    doctor = (
        db.query(User)
        .filter(User.email == login_data.email)
        .first()
    )

    if not doctor or not verify_hash(
        login_data.password,
        doctor.password_hash,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    family_id = secrets.token_urlsafe(32)

    refresh_token = create_refresh_token(
        data={
            "sub": str(doctor.user_id),
            "token_type": "refresh",
            "family_id": family_id,
        }
    )

    refresh_payload = decode_token(refresh_token)

    refresh_jti = refresh_payload["jti"]
    refresh_expiration = datetime.fromtimestamp(
        refresh_payload["exp"],
        tz=timezone.utc,
    )


    access_token = create_access_token(
        data={
            "sub": str(doctor.user_id),
            "email": doctor.email,
            "token_type": "access",
            "refresh_jti": refresh_jti,
        }
    )
    refresh_record = RefreshToken(
        jti=refresh_jti,
        family_id=family_id,
        user_id=doctor.user_id,
        expires_at=refresh_expiration,
    )

    try:
        db.add(refresh_record)
        db.commit()
    except Exception:
        db.rollback()
        raise

    return access_token, refresh_token


def forgot_password(db: Session, email: str):
    user = db.query(User).filter(User.email == email).first()

    if not user:
        return;
    
    otp = generate_OTP()
    otp_expiration = otp_expiration_time()
    otp_record = create_otp_record(db, email, otp, otp_expiration)
    
    try:
        send_otp_email(email, otp)
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send OTP email: {str(e)}",
        ) 
    
def verify_otp(
    db: Session,
    email: str,
    otp: str,
) -> str:
    otp_record = get_latest_valid_otp(
        db=db,
        email=email,
        purpose=OTPPurpose.PASSWORD_RESET,
    )

    if not otp_record or not verify_hash(otp, otp_record.otp_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP",
        )

    mark_otp_as_used(
        db=db,
        otp_id=otp_record.otp_id,
    )

    return create_access_token(
        data={
            "otp_id": otp_record.otp_id,
            "sub": email,
            "purpose": OTPPurpose.PASSWORD_RESET.value,
            "token_type": "password_reset"
        }
    )
    
def reset_password(
    db: Session,
    reset_token: str,
    new_password: str,
) -> None:
    payload = decode_token(reset_token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired reset token",
        )

    if payload.get("purpose") != OTPPurpose.PASSWORD_RESET.value:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid reset token",
        )
    
    otp_id = payload.get("otp_id")
    email = payload.get("sub")

    if not email or not otp_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid reset token",
        )

    otp_record = (
        db.query(OTPCode)
        .filter(
            OTPCode.otp_id == otp_id,
            OTPCode.email == email,
            OTPCode.purpose == OTPPurpose.PASSWORD_RESET.value,
            OTPCode.is_used.is_(True),
        )
        .with_for_update()
        .first()
    )

    if not otp_record or otp_record.reset_completed_at is not None:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Reset token has already been used or is invalid",
        )
    
    user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if not user:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    try:
        user.password_hash = hash_value(new_password)
        
        otp_record.reset_completed_at = datetime.now(timezone.utc)

        db.commit()

    except Exception:
        db.rollback()
        raise
   
    
  

def logout_user(
    db: Session,
    token: str,
) -> None:
    payload = decode_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    if payload.get("token_type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token",
        )

    jti = payload.get("jti")
    refresh_jti = payload.get("refresh_jti")
    expiration = payload.get("exp")

    if not jti or not expiration:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    already_revoked = (
        db.query(RevokedToken)
        .filter(RevokedToken.jti == jti)
        .first()
    )

    if already_revoked:
       return

    revoked_token = RevokedToken(
        jti=jti,
        expires_at=datetime.fromtimestamp(
            expiration,
            tz=timezone.utc,
        ),
    )

    db.add(revoked_token)
    
    if refresh_jti:
     refresh_record = (
        db.query(RefreshToken)
        .filter(RefreshToken.jti == refresh_jti)
        .first()
    )

    if refresh_record and refresh_record.revoked_at is None:
        refresh_record.revoked_at = datetime.now(timezone.utc)
    db.commit()
    
    
def refresh_tokens(
    db: Session,
    encoded_refresh_token: str,
) -> tuple[str, str]:
    payload = decode_token(encoded_refresh_token)

    if not payload or payload.get("token_type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    jti = payload.get("jti")
    subject = payload.get("sub")
    family_id = payload.get("family_id")

    if not jti or not subject or not family_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    try:
        user_id = int(subject)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    now = datetime.now(timezone.utc)

    refresh_record = (
        db.query(RefreshToken)
        .filter(RefreshToken.jti == jti)
        .with_for_update()
        .first()
    )

    if not refresh_record:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    if (
        refresh_record.user_id != user_id
        or refresh_record.family_id != family_id
    ):
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    if refresh_record.revoked_at is not None:
        # A rotated token was reused. Revoke the active family.
        if refresh_record.replaced_by_jti is not None:
            db.query(RefreshToken).filter(
                RefreshToken.family_id == family_id,
                RefreshToken.revoked_at.is_(None),
            ).update(
                {"revoked_at": now},
                synchronize_session=False,
            )
            db.commit()
        else:
            db.rollback()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has already been used or revoked",
        )

    if refresh_record.expires_at <= now:
        refresh_record.revoked_at = now
        db.commit()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has expired",
        )

    doctor = (
        db.query(User)
        .filter(User.user_id == user_id)
        .first()
    )

    if not doctor:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User no longer exists",
        )

    new_refresh_token = create_refresh_token(
        data={
            "sub": str(doctor.user_id),
            "token_type": "refresh",
            "family_id": family_id,
        }
    )

    new_payload = decode_token(new_refresh_token)
    new_jti = new_payload["jti"]

    new_record = RefreshToken(
        jti=new_jti,
        family_id=family_id,
        user_id=doctor.user_id,
        expires_at=datetime.fromtimestamp(
            new_payload["exp"],
            tz=timezone.utc,
        ),
    )

    new_access_token = create_access_token(
        data={
            "sub": str(doctor.user_id),
            "email": doctor.email,
            "token_type": "access",
            "refresh_jti": new_jti,
        }
    )

    refresh_record.revoked_at = now
    refresh_record.replaced_by_jti = new_jti

    try:
        db.add(new_record)
        db.commit()
    except Exception:
        db.rollback()
        raise

    return new_access_token, new_refresh_token