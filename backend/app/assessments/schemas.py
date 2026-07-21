from datetime import date
from decimal import Decimal

from pydantic import BaseModel


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
    fast_food: bool
    regular_exercise: bool

    follicle_left: int
    follicle_right: int

    prediction_probability: Decimal | None = None
    prediction_class: str | None = None
    doctor_notes: str | None = None