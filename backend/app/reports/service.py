from datetime import date
from decimal import Decimal
from io import BytesIO

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.assessments.models import (
    Assessment,
    AssessmentResult,
)
from app.patients.models import Patient
from app.reports.assessment_report import AssessmentReport
from app.users.models import User


def calculate_age(
    date_of_birth: date,
    assessment_date: date,
) -> int:
    return (
        assessment_date.year
        - date_of_birth.year
        - (
            (
                assessment_date.month,
                assessment_date.day,
            )
            < (
                date_of_birth.month,
                date_of_birth.day,
            )
        )
    )


def build_assessment_report(
    db: Session,
    patient_id: int,
    assessment_id: int,
    current_doctor: User,
) -> BytesIO:
    row = (
        db.query(
            Patient,
            Assessment,
            AssessmentResult,
        )
        .join(
            Assessment,
            Assessment.patient_id == Patient.patient_id,
        )
        .join(
            AssessmentResult,
            AssessmentResult.assessment_id
            == Assessment.assessment_id,
        )
        .filter(
            Patient.patient_id == patient_id,
            Patient.doctor_id == current_doctor.user_id,
            Assessment.assessment_id == assessment_id,
        )
        .first()
    )

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment report not found",
        )

    patient, assessment, result = row

    height_m = (
        patient.height_cm / Decimal("100")
    )

    bmi = (
        assessment.weight_kg
        / (height_m * height_m)
    ).quantize(Decimal("0.01"))

    report_data = {
        "doctor_name": (
            f"Dr. {current_doctor.first_name} "
            f"{current_doctor.last_name}"
        ),
        "doctor_specialization": (
            current_doctor.specialization
        ),
        "doctor_hospital": (
            current_doctor.hospital
            or "Independent Clinic"
        ),
        "doctor_clinic_address": (
            current_doctor.clinic_address
        ),
        "doctor_license_number": (
            current_doctor.license_number
        ),

        "patient_id": patient.patient_id,
        "patient_name": (
            f"{patient.first_name} "
            f"{patient.last_name}"
        ),
        "date_of_birth": patient.date_of_birth,
        "age": calculate_age(
            patient.date_of_birth,
            assessment.assessment_date,
        ),
        "patient_email": patient.email,
        "height_cm": patient.height_cm,

        "assessment_id": assessment.assessment_id,
        "assessment_date": assessment.assessment_date,
        "weight_kg": assessment.weight_kg,
        "bmi": bmi,
        "cycle_regular": assessment.cycle_regular,
        "cycle_length": assessment.cycle_length,

        "fsh_miu_ml": assessment.fsh_miu_ml,
        "lh_miu_ml": assessment.lh_miu_ml,
        "fsh_lh_ratio": assessment.fsh_lh_ratio,
        "amh_ng_ml": assessment.amh_ng_ml,

        "weight_gain": assessment.weight_gain,
        "hair_growth": assessment.hair_growth,
        "skin_darkening": assessment.skin_darkening,
        "hair_loss": assessment.hair_loss,
        "pimples": assessment.pimples,

        "fast_food": assessment.fast_food,
        "regular_exercise": (
            assessment.regular_exercise
        ),

        "follicle_left": assessment.follicle_left,
        "follicle_right": assessment.follicle_right,
        "total_follicles": (
            assessment.follicle_left
            + assessment.follicle_right
        ),
        "follicle_difference": abs(
            assessment.follicle_left
            - assessment.follicle_right
        ),

        "prediction_class": result.prediction_class,
        "prediction_probability": (
            result.prediction_probability
        ),
        "doctor_notes": result.doctor_notes,
    }

    report = AssessmentReport()

    return report.build_pdf(report_data)