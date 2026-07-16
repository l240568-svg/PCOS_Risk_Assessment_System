from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.auth.schemas import LoginRequest, RegisterRequest
from app.auth.utils import create_access_token, hash_password, validate_password_strength,verify_password
from app.users.models import User


def register_doctor(db: Session, doctor_data: RegisterRequest) -> User:
    existing_email = db.query(User).filter(User.email == doctor_data.email).first()

    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    existing_license = (
        db.query(User)
        .filter(User.license_number == doctor_data.license_number)
        .first()
    )

    if existing_license:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="License number already registered",
        )

    if doctor_data.specialization not in ["Gynecologist", "Endocrinologist"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid specialization",
        )
    
    try:
        validate_password_strength(doctor_data.password)
    except ValueError as error:
        raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=str(error),
    )

    new_doctor = User(
        first_name=doctor_data.first_name,
        last_name=doctor_data.last_name,
        email=doctor_data.email,
        specialization=doctor_data.specialization,
        hospital=doctor_data.hospital,
        clinic_address=doctor_data.clinic_address,
        license_number=doctor_data.license_number,
        password_hash=hash_password(doctor_data.password),
    )

    db.add(new_doctor)
    db.commit()
    db.refresh(new_doctor)

    return new_doctor


def login_doctor(db: Session, login_data: LoginRequest) -> str:
    doctor = db.query(User).filter(User.email == login_data.email).first()

    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not verify_password(login_data.password, doctor.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    access_token = create_access_token(
        data={
            "sub": str(doctor.user_id),
            "email": doctor.email,
        }
    )

    return access_token