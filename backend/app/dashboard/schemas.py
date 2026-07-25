from datetime import date
from decimal import Decimal

from pydantic import BaseModel

from app.patients.schemas import PatientResponse
from app.users.schemas import UserResponse


class DashboardSummary(BaseModel):
    total_patients: int
    total_assessments: int
    high_risk_patients: int
    low_risk_patients: int
    unassessed_patients: int


class DashboardPatientAssessment(BaseModel):
    patient: PatientResponse

    assessment_id: int
    assessment_date: date

    result_id: int | None = None
    prediction_probability: Decimal | None = None
    prediction_class: str | None = None
    doctor_notes: str | None = None


class DashboardResponse(BaseModel):
    doctor_profile: UserResponse
    summary: DashboardSummary

    patients_needing_attention: list[
        DashboardPatientAssessment
    ]

    recently_assessed_patients: list[
        DashboardPatientAssessment
    ]