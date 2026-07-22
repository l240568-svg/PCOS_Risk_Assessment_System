from datetime import date
from decimal import Decimal

from sqlalchemy import Boolean, Date, ForeignKey, Numeric, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Assessment(Base):
    __tablename__ = "assessments"

    assessment_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    patient_id: Mapped[int] = mapped_column(
        ForeignKey("patients.patient_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    assessment_date: Mapped[date] = mapped_column(Date, server_default=text("CURRENT_DATE"))

    weight_kg: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    cycle_regular: Mapped[bool] = mapped_column(Boolean, nullable=False)
    cycle_length: Mapped[int] = mapped_column(nullable=False)

    fsh_miu_ml: Mapped[Decimal] = mapped_column(Numeric(6, 2), nullable=False)
    lh_miu_ml: Mapped[Decimal] = mapped_column(Numeric(6, 2), nullable=False)
    amh_ng_ml: Mapped[Decimal | None] = mapped_column(Numeric(6, 2))
    fsh_lh_ratio: Mapped[Decimal | None] = mapped_column(Numeric(6, 2))

    weight_gain: Mapped[bool] = mapped_column(Boolean, nullable=False)
    hair_growth: Mapped[bool] = mapped_column(Boolean, nullable=False)
    skin_darkening: Mapped[bool] = mapped_column(Boolean, nullable=False)
    hair_loss: Mapped[bool] = mapped_column(Boolean, nullable=False)
    pimples: Mapped[bool] = mapped_column(Boolean, nullable=False)
    
    fast_food: Mapped[bool] = mapped_column(Boolean, nullable=False)
    regular_exercise: Mapped[bool] = mapped_column(Boolean, nullable=False)

    follicle_left: Mapped[int] = mapped_column(nullable=False)
    follicle_right: Mapped[int] = mapped_column(nullable=False)


class AssessmentResult(Base):
    __tablename__ = "assessment_results"

    result_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    assessment_id: Mapped[int] = mapped_column(
        ForeignKey("assessments.assessment_id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    prediction_probability: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False)
    prediction_class: Mapped[str] = mapped_column(String(20), nullable=False)
    doctor_notes: Mapped[str | None] = mapped_column(Text)