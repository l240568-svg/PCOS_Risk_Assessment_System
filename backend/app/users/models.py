from datetime import date

from sqlalchemy import CheckConstraint, Date, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(primary_key=True, index=True)

    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)

    specialization: Mapped[str] = mapped_column(String(50), nullable=False)
    hospital: Mapped[str | None] = mapped_column(String(100))
    clinic_address: Mapped[str | None] = mapped_column(String(150))

    license_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    created_at: Mapped[date] = mapped_column(Date, server_default=text("CURRENT_DATE"))
    updated_at: Mapped[date] = mapped_column(Date, server_default=text("CURRENT_DATE"))

    __table_args__ = (
        CheckConstraint(
            "specialization IN ('Gynecologist', 'Endocrinologist')",
            name="chk_specialization",
        ),
    )