from enum import Enum
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.auth.models import OTPCode
from app.auth.utils import hash_value

class OTPPurpose(str, Enum):
    PASSWORD_RESET = "PASSWORD_RESET"
    EMAIL_VERIFICATION = "EMAIL_VERIFICATION"

def create_otp_record(
    db: Session, email: str, otp: str, expiration_time: datetime
):
    otp_hash = hash_value(otp)
    otp_record = OTPCode(
        email=email,
        otp_hash=otp_hash,
        purpose=OTPPurpose.PASSWORD_RESET,
        expires_at=expiration_time,
    )
    db.add(otp_record)
    db.commit()
    db.refresh(otp_record)
    return otp_record

def get_latest_valid_otp(
    db: Session,
    email: str,
    purpose: OTPPurpose
):
    now = datetime.now(timezone.utc)
    return (
        db.query(OTPCode)
        .filter(
            OTPCode.email == email,
            OTPCode.purpose == purpose,
            OTPCode.expires_at > now,
            OTPCode.is_used == False,
        )
        .order_by(OTPCode.created_at.desc())
        .first()
    )
    
def mark_otp_as_used(
    db: Session,
    otp_id: int,
) -> None:
    otp_record = (
        db.query(OTPCode)
        .filter(
            OTPCode.otp_id == otp_id,
            OTPCode.is_used.is_(False),
        )
        .first()
    )

    if otp_record:
        otp_record.is_used = True
        db.commit()