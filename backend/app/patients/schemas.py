from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class PatientCreateRequest(BaseModel):
    first_name: str = Field(min_length=1, max_length=50)
    last_name: str = Field(min_length=1, max_length=50)
    email: EmailStr | None = None
    date_of_birth: date
    height_cm: Decimal = Field(ge=80, le=250)


class PatientResponse(BaseModel):
    patient_id: int
    doctor_id: int
    first_name: str
    last_name: str
    email: EmailStr | None = None
    date_of_birth: date
    height_cm: Decimal
    created_at: date

    model_config = ConfigDict(from_attributes=True)


class PatientUpdateRequest(BaseModel):
    first_name: str | None = Field(default=None, min_length=1, max_length=50)
    last_name: str | None = Field(default=None, min_length=1, max_length=50)
    email: EmailStr | None = None
    date_of_birth: date | None = None
    height_cm: Decimal | None = Field(default=None, ge=80, le=250)