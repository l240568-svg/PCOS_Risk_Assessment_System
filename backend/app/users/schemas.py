from datetime import date

from pydantic import BaseModel, ConfigDict, EmailStr


class UserResponse(BaseModel):
    user_id: int
    first_name: str
    last_name: str
    email: EmailStr
    specialization: str
    hospital: str | None = None
    clinic_address: str | None = None
    license_number: str
    created_at: date

    model_config = ConfigDict(from_attributes=True)