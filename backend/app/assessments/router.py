from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.assessments import schemas, service
from app.core.dependencies import get_current_doctor, get_db
from app.users.models import User


router = APIRouter(
    prefix="/patients/{patient_id}/assessments",
    tags=["Assessments"],
)


@router.get(
    "/",
    response_model=list[schemas.AssessmentWithResultResponse],
)
def get_patient_assessments(
    patient_id: int,
    limit: int | None = Query(default=None, ge=1, le=100),
    db: Session = Depends(get_db),
    current_doctor: User = Depends(get_current_doctor),
):
    return service.get_patient_assessments(
        db=db,
        patient_id=patient_id,
        current_doctor=current_doctor,
        limit=limit,
    )


@router.get(
    "/{assessment_id}",
    response_model=schemas.AssessmentWithResultResponse,
)
def get_assessment_detail(
    patient_id: int,
    assessment_id: int,
    db: Session = Depends(get_db),
    current_doctor: User = Depends(get_current_doctor),
):
    return service.get_assessment_detail(
        db=db,
        patient_id=patient_id,
        assessment_id=assessment_id,
        current_doctor=current_doctor,
    )


@router.delete(
    "/{assessment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_assessment(
    patient_id: int,
    assessment_id: int,
    db: Session = Depends(get_db),
    current_doctor: User = Depends(get_current_doctor),
):
    service.delete_assessment(
        db=db,
        patient_id=patient_id,
        assessment_id=assessment_id,
        current_doctor=current_doctor,
    )
    
@router.post(
    "/",
    response_model=schemas.AssessmentWithResultResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_assessment(
    patient_id: int,
    assessment_data: schemas.AssessmentCreateRequest,
    db: Session = Depends(get_db),
    current_doctor: User = Depends(get_current_doctor),
):
    return service.create_assessment(
        db=db,
        patient_id=patient_id,
        data=assessment_data,
        current_doctor=current_doctor,
    )