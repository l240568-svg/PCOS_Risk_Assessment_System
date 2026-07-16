from datetime import datetime

from sqlalchemy import Boolean, DateTime, Identity, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class OTPCode(Base):
    __tablename__ = "otp_codes"

    otp_id: Mapped[int] = mapped_column(
        Identity(always=True),
        primary_key=True,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        index=True,
        nullable=False,
    )

    # The hashed OTP code, not the plain text code for security reasons
    otp_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    
    purpose: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    is_used: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )