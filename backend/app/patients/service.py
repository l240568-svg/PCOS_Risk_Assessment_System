from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.assessments.models import Assessment, AssessmentResult
from app.patients.models import Patient
from app.patients.schemas import PatientCreateRequest,PatientUpdateRequest
from app.users.models import User


def create_patient(
    db: Session,
    patient_data: PatientCreateRequest,
    current_doctor: User,
) -> Patient:
    new_patient = Patient(
        doctor_id=current_doctor.user_id,
        first_name=patient_data.first_name,
        last_name=patient_data.last_name,
        email=patient_data.email,
        date_of_birth=patient_data.date_of_birth,
        height_cm=patient_data.height_cm,
    )

    db.add(new_patient)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Patient email already exists",
        )

    db.refresh(new_patient)
    return new_patient


def get_my_patients(db: Session, current_doctor: User) -> list[Patient]:
    return (
        db.query(Patient)
        .filter(Patient.doctor_id == current_doctor.user_id)
        .order_by(Patient.created_at.desc(), Patient.patient_id.desc())
        .all()
    )


def delete_patient(
    db: Session,
    patient_id: int,
    current_doctor: User,
) -> None:
    patient = (
        db.query(Patient)
        .filter(
            Patient.patient_id == patient_id,
            Patient.doctor_id == current_doctor.user_id,
        )
        .first()
    )

    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )

    db.delete(patient)
    db.commit()


def search_patients(
    db: Session,
    current_doctor: User,
    name: str | None = None,
    prediction_class: str | None = None,
) -> list[Patient]:
    query = db.query(Patient).filter(Patient.doctor_id == current_doctor.user_id)

    if name:
        search_text = f"%{name}%"
        query = query.filter(
            or_(
                Patient.first_name.ilike(search_text),
                Patient.last_name.ilike(search_text),
            )
        )

    if prediction_class:
        query = (
            query.join(Assessment, Assessment.patient_id == Patient.patient_id)
            .join(
                AssessmentResult,
                AssessmentResult.assessment_id == Assessment.assessment_id,
            )
            .filter(AssessmentResult.prediction_class == prediction_class)
            .distinct()
        )

    return (
        query.order_by(Patient.created_at.desc(), Patient.patient_id.desc())
        .all()
    )

def get_patient_detail(
    db: Session,
    patient_id: int,
    current_doctor: User,
) -> Patient:
    patient = (
        db.query(Patient)
        .filter(
            Patient.patient_id == patient_id,
            Patient.doctor_id == current_doctor.user_id,
        )
        .first()
    )

    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )

    return patient


def update_patient(
    db: Session,
    patient_id: int,
    patient_data: PatientUpdateRequest,
    current_doctor: User,
) -> Patient:
    patient = get_patient_detail(db, patient_id, current_doctor)

    update_data = patient_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(patient, field, value)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Patient email already exists",
        )

    db.refresh(patient)
    return patient