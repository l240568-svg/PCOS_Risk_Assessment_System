from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.assessments.models import Assessment, AssessmentResult
from app.patients.models import Patient
from app.users.models import User


def get_patient_for_current_doctor(
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


def format_assessment_response(
    assessment: Assessment,
    result: AssessmentResult | None,
) -> dict:
    return {
        "assessment_id": assessment.assessment_id,
        "patient_id": assessment.patient_id,
        "assessment_date": assessment.assessment_date,
        "weight_kg": assessment.weight_kg,
        "cycle_regular": assessment.cycle_regular,
        "cycle_length": assessment.cycle_length,
        "fsh_miu_ml": assessment.fsh_miu_ml,
        "lh_miu_ml": assessment.lh_miu_ml,
        "amh_ng_ml": assessment.amh_ng_ml,
        "fsh_lh_ratio": assessment.fsh_lh_ratio,
        "weight_gain": assessment.weight_gain,
        "hair_growth": assessment.hair_growth,
        "skin_darkening": assessment.skin_darkening,
        "fast_food": assessment.fast_food,
        "regular_exercise": assessment.regular_exercise,
        "follicle_left": assessment.follicle_left,
        "follicle_right": assessment.follicle_right,
        "prediction_probability": result.prediction_probability if result else None,
        "prediction_class": result.prediction_class if result else None,
        "doctor_notes": result.doctor_notes if result else None,
    }


def get_patient_assessments(
    db: Session,
    patient_id: int,
    current_doctor: User,
    limit: int | None = None,
) -> list[dict]:
    get_patient_for_current_doctor(db, patient_id, current_doctor)

    query = (
        db.query(Assessment, AssessmentResult)
        .outerjoin(
            AssessmentResult,
            AssessmentResult.assessment_id == Assessment.assessment_id,
        )
        .filter(Assessment.patient_id == patient_id)
        .order_by(Assessment.assessment_date.desc(), Assessment.assessment_id.desc())
    )

    if limit:
        query = query.limit(limit)

    rows = query.all()

    return [
        format_assessment_response(assessment, result)
        for assessment, result in rows
    ]


def get_assessment_detail(
    db: Session,
    patient_id: int,
    assessment_id: int,
    current_doctor: User,
) -> dict:
    get_patient_for_current_doctor(db, patient_id, current_doctor)

    row = (
        db.query(Assessment, AssessmentResult)
        .outerjoin(
            AssessmentResult,
            AssessmentResult.assessment_id == Assessment.assessment_id,
        )
        .filter(
            Assessment.patient_id == patient_id,
            Assessment.assessment_id == assessment_id,
        )
        .first()
    )

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found",
        )

    assessment, result = row
    return format_assessment_response(assessment, result)


def delete_assessment(
    db: Session,
    patient_id: int,
    assessment_id: int,
    current_doctor: User,
) -> None:
    get_patient_for_current_doctor(db, patient_id, current_doctor)

    assessment = (
        db.query(Assessment)
        .filter(
            Assessment.patient_id == patient_id,
            Assessment.assessment_id == assessment_id,
        )
        .first()
    )

    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found",
        )

    db.delete(assessment)
    db.commit()