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