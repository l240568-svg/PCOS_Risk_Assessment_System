from datetime import date
from pydantic import BaseModel, ConfigDict, EmailStr, Field


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


class UserUpdateRequest(BaseModel):
    first_name: str | None = Field(default=None, min_length=1, max_length=50)
    last_name: str | None = Field(default=None, min_length=1, max_length=50)
    email: EmailStr | None = None
    specialization: str | None = None
    hospital: str | None = Field(default=None, max_length=100)
    clinic_address: str | None = Field(default=None, max_length=150)
    license_number: str | None = Field(default=None, min_length=1, max_length=50)


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str = Field(min_length=8, max_length=72)
    confirm_new_password: str = Field(min_length=8, max_length=72)