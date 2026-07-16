from core.database import engine
from app.auth.models import OTPCode

def create_otp_table() -> None:
    OTPCode.__table__.create(
        bind=engine,
        checkfirst=True,
    )


if __name__ == "__main__":
    create_otp_table()