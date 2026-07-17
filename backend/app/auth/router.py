from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.auth import schemas, service
from app.core.dependencies import get_db
from app.users.schemas import UserResponse


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_doctor(
    doctor_data: schemas.RegisterRequest,
    db: Session = Depends(get_db),
):
    return service.register_doctor(db, doctor_data)


@router.post(
    "/login",
    response_model=schemas.TokenResponse,
)
def login_doctor(
    login_data: schemas.LoginRequest,
    db: Session = Depends(get_db),
):
    access_token = service.login_doctor(db, login_data)

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }

@router.post(
    "/forgot-password",
    status_code=status.HTTP_200_OK,
)
def forgot_password(
    request: schemas.ForgotPasswordRequest,
    db: Session = Depends(get_db),
):
    service.forgot_password(db, request.email)
    return {"message": "If an account exists with this email, "
            "an OTP has been sent."}
    
    
@router.post(
    "/verify-otp",
    response_model=schemas.OTPVerificationResponse,
)
def verify_otp(
    request: schemas.OTPVerificationRequest,
    db: Session = Depends(get_db),
):
    reset_token = service.verify_otp(db,request.email, request.otp)
    return {
        "reset_token": reset_token,
        "token_type": "bearer",
    }

@router.patch(
    "/reset-password",
    status_code=status.HTTP_200_OK,
)
def reset_password(
    request: schemas.ResetPasswordRequest,
    db: Session = Depends(get_db),
):
    service.reset_password(db, request.reset_token, request.new_password)
    return {"message": "Password has been reset successfully."}