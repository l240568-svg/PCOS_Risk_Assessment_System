from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field


class AssessmentWithResultResponse(BaseModel):
    assessment_id: int
    patient_id: int
    assessment_date: date

    weight_kg: Decimal
    cycle_regular: bool
    cycle_length: int

    fsh_miu_ml: Decimal
    lh_miu_ml: Decimal
    amh_ng_ml: Decimal | None = None
    fsh_lh_ratio: Decimal | None = None

    weight_gain: bool
    hair_growth: bool
    skin_darkening: bool
    hair_loss: bool
    pimples: bool
    fast_food: bool
    regular_exercise: bool

    follicle_left: int
    follicle_right: int

    prediction_probability: Decimal | None = None
    prediction_class: str | None = None
    doctor_notes: str | None = None
    


class AssessmentCreateRequest(BaseModel):
    weight_kg: Decimal = Field(ge=20, le=300)

    cycle_regular: bool
    cycle_length: int = Field(ge=15, le=120)

    fsh_miu_ml: Decimal = Field(ge=0, le=200)
    lh_miu_ml: Decimal = Field(ge=0, le=200)
    amh_ng_ml: Decimal | None = Field(
        default=None,
        ge=0,
        le=50,
    )

    weight_gain: bool
    hair_growth: bool
    skin_darkening: bool
    hair_loss: bool
    pimples: bool

    fast_food: bool
    regular_exercise: bool

    follicle_left: int = Field(ge=0, le=50)
    follicle_right: int = Field(ge=0, le=50)

    doctor_notes: str | None = Field(
        default=None,
        max_length=5000,
    )