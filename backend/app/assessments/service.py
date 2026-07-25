from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.assessments.models import Assessment, AssessmentResult
from app.patients.models import Patient
from app.users.models import User

from datetime import date
from decimal import Decimal

from app.assessments.features import build_model_features
from app.assessments.schemas import AssessmentCreateRequest, AssessmentNotesUpdateRequest
from app.ml.predictor import predict_pcos_risk

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
        "hair_loss": assessment.hair_loss,
        "pimples": assessment.pimples,
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
    
    
def create_assessment(
    db: Session,
    patient_id: int,
    data: AssessmentCreateRequest,
    current_doctor: User,
) -> dict:
    patient = get_patient_for_current_doctor(
        db=db,
        patient_id=patient_id,
        current_doctor=current_doctor,
    )

    assessment_date = date.today()

    model_features, fsh_lh_ratio = build_model_features(
        patient=patient,
        data=data,
        assessment_date=assessment_date,
    )

    try:
        probability, prediction_class = predict_pcos_risk(
            model_features
        )
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="PCOS prediction model is unavailable",
        ) from error

    assessment = Assessment(
        patient_id=patient.patient_id,
        assessment_date=assessment_date,
        weight_kg=data.weight_kg,
        cycle_regular=data.cycle_regular,
        cycle_length=data.cycle_length,
        fsh_miu_ml=data.fsh_miu_ml,
        lh_miu_ml=data.lh_miu_ml,
        amh_ng_ml=data.amh_ng_ml,
        fsh_lh_ratio=fsh_lh_ratio,
        weight_gain=data.weight_gain,
        hair_growth=data.hair_growth,
        skin_darkening=data.skin_darkening,
        hair_loss=data.hair_loss,
        pimples=data.pimples,
        fast_food=data.fast_food,
        regular_exercise=data.regular_exercise,
        follicle_left=data.follicle_left,
        follicle_right=data.follicle_right,
    )

    try:
        db.add(assessment)
        db.flush()

        result = AssessmentResult(
            assessment_id=assessment.assessment_id,
            prediction_probability=Decimal(
                str(probability)
            ).quantize(Decimal("0.0001")),
            prediction_class=prediction_class,
            doctor_notes=data.doctor_notes,
        )

        db.add(result)
        db.commit()

        db.refresh(assessment)
        db.refresh(result)

    except Exception:
        db.rollback()
        raise

    return format_assessment_response(
        assessment=assessment,
        result=result,
    )

def update_assessment_notes(
    db: Session,
    patient_id: int,
    assessment_id: int,
    data: AssessmentNotesUpdateRequest,
    current_doctor: User,
) -> dict:
    get_patient_for_current_doctor(
        db=db,
        patient_id=patient_id,
        current_doctor=current_doctor,
    )

    row = (
        db.query(Assessment, AssessmentResult)
        .join(
            AssessmentResult,
            AssessmentResult.assessment_id
            == Assessment.assessment_id,
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

    result.doctor_notes = (
        data.doctor_notes.strip()
        if data.doctor_notes
        else None
    )

    try:
        db.commit()
        db.refresh(result)
    except Exception:
        db.rollback()
        raise

    return format_assessment_response(
        assessment=assessment,
        result=result,
    )