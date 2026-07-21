from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Identity, PrimaryKeyConstraint, String, func
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
    
    reset_completed_at: Mapped[datetime | None] = mapped_column(
    DateTime(timezone=True),
    nullable=True,
    )
    
    
class RevokedToken(Base):
    __tablename__ = "revoked_tokens"
    
    #unique identifier for the JWT token
    jti: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False,
        primary_key=True, 
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    revoked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
   
class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    jti: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
    )

    family_id: Mapped[str] = mapped_column(
        String(64),
        index=True,
        nullable=False,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    replaced_by_jti: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )