from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_doctor, get_db
from app.users import schemas, service
from app.users.models import User


router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.get(
    "/me",
    response_model=schemas.UserResponse,
)
def get_user_profile(
    current_doctor: User = Depends(get_current_doctor),
):
    return service.get_user_profile(current_doctor)


@router.patch(
    "/me",
    response_model=schemas.UserResponse,
)
def update_user_profile(
    user_data: schemas.UserUpdateRequest,
    db: Session = Depends(get_db),
    current_doctor: User = Depends(get_current_doctor),
):
    return service.update_user_profile(db, user_data, current_doctor)


@router.patch(
    "/me/password",
    status_code=status.HTTP_200_OK,
)
def change_password(
    password_data: schemas.ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_doctor: User = Depends(get_current_doctor),
):
    service.change_password(db, password_data, current_doctor)
    return {"message": "Password changed successfully"}