from app.core.database import engine
from app.auth.models import OTPCode, RevokedToken

def create_otp_table() -> None:
    OTPCode.__table__.create(
        bind=engine,
        checkfirst=True,
    )


def create_revoked_tokens_table() -> None:
    RevokedToken.__table__.create(
        bind=engine,
        checkfirst=True,
    )