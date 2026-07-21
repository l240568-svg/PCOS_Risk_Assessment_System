
import datetime
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.auth.schemas import LoginRequest, RegisterRequest, OTPVerificationRequest
from app.auth.utils import create_access_token, hash_value, validate_password_strength, verify_hash, generate_OTP, otp_expiration_time, decode_access_token
from app.users.models import User
from app.auth.otp_service import create_otp_record, get_latest_valid_otp, mark_otp_as_used
from app.emails.email_service import send_otp_email
from app.auth.otp_service import OTPPurpose
from app.auth.models import OTPCode
from app.auth.models import RevokedToken




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


def login_doctor(db: Session, login_data: LoginRequest) -> str:
    doctor = db.query(User).filter(User.email == login_data.email).first()

    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )


    if not verify_hash(login_data.password, doctor.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    access_token = create_access_token(
        data={
            "sub": str(doctor.user_id),
            "email": doctor.email,
            "token_type": "access"
        }
    )

    return access_token


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
    payload = decode_access_token(reset_token)

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
    payload = decode_access_token(token)

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
    db.commit()