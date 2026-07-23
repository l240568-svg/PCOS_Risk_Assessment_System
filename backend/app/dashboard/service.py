from sqlalchemy import and_, case, func
from sqlalchemy.orm import Session

from app.assessments.models import Assessment, AssessmentResult
from app.patients.models import Patient
from app.users.models import User


def build_latest_assessment_subquery(
    db: Session,
):
    return (
        db.query(
            Assessment.patient_id.label("patient_id"),
            Assessment.assessment_id.label("assessment_id"),
            Assessment.assessment_date.label("assessment_date"),
            AssessmentResult.result_id.label("result_id"),
            AssessmentResult.prediction_probability.label(
                "prediction_probability"
            ),
            AssessmentResult.prediction_class.label(
                "prediction_class"
            ),
            func.row_number()
            .over(
                partition_by=Assessment.patient_id,
                order_by=(
                    Assessment.assessment_date.desc(),
                    Assessment.assessment_id.desc(),
                ),
            )
            .label("row_number"),
        )
        .outerjoin(
            AssessmentResult,
            AssessmentResult.assessment_id
            == Assessment.assessment_id,
        )
        .subquery()
    )


def format_patient_assessment(row) -> dict:
    (
        patient,
        assessment_id,
        assessment_date,
        result_id,
        probability,
        prediction_class,
        doctor_notes,
    ) = row

    return {
        "patient": patient,
        "assessment_id": assessment_id,
        "assessment_date": assessment_date,
        "result_id": result_id,
        "prediction_probability": probability,
        "prediction_class": prediction_class,
        "doctor_notes": doctor_notes,
    }


def get_dashboard(
    db: Session,
    current_doctor: User,
) -> dict:
    latest = build_latest_assessment_subquery(db)

    summary_row = (
        db.query(
            func.count(Patient.patient_id).label(
                "total_patients"
            ),
            func.count(latest.c.assessment_id).label(
                "assessed_patients"
            ),
            func.count(
                case(
                    (
                        latest.c.prediction_class == "High Risk",
                        1,
                    )
                )
            ).label("high_risk_patients"),
            func.count(
                case(
                    (
                        latest.c.prediction_class == "Low Risk",
                        1,
                    )
                )
            ).label("low_risk_patients"),
        )
        .outerjoin(
            latest,
            and_(
                latest.c.patient_id == Patient.patient_id,
                latest.c.row_number == 1,
            ),
        )
        .filter(
            Patient.doctor_id == current_doctor.user_id
        )
        .one()
    )

    total_patients = int(summary_row.total_patients or 0)
    assessed_patients = int(summary_row.assessed_patients or 0)

    total_assessments = (
        db.query(func.count(Assessment.assessment_id))
        .join(
            Patient,
            Patient.patient_id == Assessment.patient_id,
        )
        .filter(
            Patient.doctor_id == current_doctor.user_id
        )
        .scalar()
        or 0
    )

    result_columns = (
        latest.c.assessment_id,
        latest.c.assessment_date,
        latest.c.result_id,
        latest.c.prediction_probability,
        latest.c.prediction_class,
        latest.c.doctor_notes,
    )

    attention_rows = (
        db.query(
            Patient,
            *result_columns,
        )
        .join(
            latest,
            and_(
                latest.c.patient_id == Patient.patient_id,
                latest.c.row_number == 1,
            ),
        )
        .filter(
            Patient.doctor_id == current_doctor.user_id,
            latest.c.prediction_class == "High Risk",
        )
        .order_by(
            latest.c.prediction_probability.desc(),
            latest.c.assessment_date.desc(),
            latest.c.assessment_id.desc(),
        )
        .all()
    )

    recent_rows = (
        db.query(
            Patient,
            *result_columns,
        )
        .join(
            latest,
            and_(
                latest.c.patient_id == Patient.patient_id,
                latest.c.row_number == 1,
            ),
        )
        .filter(
            Patient.doctor_id == current_doctor.user_id
        )
        .order_by(
            latest.c.assessment_date.desc(),
            latest.c.assessment_id.desc(),
        )
        .limit(5)
        .all()
    )

    return {
        "doctor_profile": current_doctor,
        "summary": {
            "total_patients": total_patients,
            "total_assessments": int(total_assessments),
            "high_risk_patients": int(
                summary_row.high_risk_patients or 0
            ),
            "low_risk_patients": int(
                summary_row.low_risk_patients or 0
            ),
            "unassessed_patients": (
                total_patients - assessed_patients
            ),
        },
        "patients_needing_attention": [
            format_patient_assessment(row)
            for row in attention_rows
        ],
        "recently_assessed_patients": [
            format_patient_assessment(row)
            for row in recent_rows
        ],
    }