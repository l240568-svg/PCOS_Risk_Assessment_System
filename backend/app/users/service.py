from datetime import date

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth.utils import hash_value, validate_password_strength, verify_hash
from app.users.models import User
from app.users.schemas import ChangePasswordRequest, UserUpdateRequest


def get_user_profile(current_doctor: User) -> User:
    return current_doctor


def update_user_profile(
    db: Session,
    user_data: UserUpdateRequest,
    current_doctor: User,
) -> User:
    update_data = user_data.model_dump(exclude_unset=True)

    if "specialization" in update_data:
        if update_data["specialization"] not in ["Gynecologist", "Endocrinologist"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid specialization",
            )

    for field, value in update_data.items():
        setattr(current_doctor, field, value)

    current_doctor.updated_at = date.today()

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or license number already exists",
        )

    db.refresh(current_doctor)
    return current_doctor


def change_password(
    db: Session,
    password_data: ChangePasswordRequest,
    current_doctor: User,
) -> None:
    if not verify_hash(password_data.old_password, current_doctor.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Old password is incorrect",
        )

    if password_data.new_password != password_data.confirm_new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password and confirm password do not match",
        )

    try:
        validate_password_strength(password_data.new_password)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )

    current_doctor.password_hash = hash_value(password_data.new_password)
    current_doctor.updated_at = date.today()

    db.commit()