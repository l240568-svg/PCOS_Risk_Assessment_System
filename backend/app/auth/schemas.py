from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    first_name: str = Field(min_length=1, max_length=50)
    last_name: str = Field(min_length=1, max_length=50)
    email: EmailStr

    specialization: str
    hospital: str | None = Field(default=None, max_length=100)
    clinic_address: str | None = Field(default=None, max_length=150)

    license_number: str = Field(min_length=1, max_length=50)

    password: str = Field(min_length=8, max_length=72)


class LoginRequest(BaseModel):
    email: EmailStr 
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    
class ForgotPasswordRequest(BaseModel):
    email: EmailStr
    
class OTPVerificationRequest(BaseModel):
    email: EmailStr
    otp: str = Field(
        min_length=6,
        max_length=6,
        pattern=r"^\d{6}$",
    )

class OTPVerificationResponse(BaseModel):
    reset_token: str
    token_type: str = "bearer"
    
class ResetPasswordRequest(BaseModel):
    reset_token: str
    new_password: str = Field(min_length=8, max_length=72)