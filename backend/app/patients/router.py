from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_doctor, get_db
from app.patients import schemas, service
from app.users.models import User


router = APIRouter(
    prefix="/patients",
    tags=["Patients"],
)


@router.post(
    "/",
    response_model=schemas.PatientResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_patient(
    patient_data: schemas.PatientCreateRequest,
    db: Session = Depends(get_db),
    current_doctor: User = Depends(get_current_doctor),
):
    return service.create_patient(db, patient_data, current_doctor)


@router.get(
    "/",
    response_model=list[schemas.PatientResponse],
)
def get_my_patients(
    db: Session = Depends(get_db),
    current_doctor: User = Depends(get_current_doctor),
):
    return service.get_my_patients(db, current_doctor)


@router.get(
    "/search",
    response_model=list[schemas.PatientResponse],
)
def search_patients(
    name: str | None = Query(default=None, min_length=1),
    prediction_class: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_doctor: User = Depends(get_current_doctor),
):
    return service.search_patients(
        db=db,
        current_doctor=current_doctor,
        name=name,
        prediction_class=prediction_class,
    )


@router.delete(
    "/{patient_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_doctor: User = Depends(get_current_doctor),
):
    service.delete_patient(db, patient_id, current_doctor)


@router.get(
    "/{patient_id}",
    response_model=schemas.PatientResponse,
)
def get_patient_detail(
    patient_id: int,
    db: Session = Depends(get_db),
    current_doctor: User = Depends(get_current_doctor),
):
    return service.get_patient_detail(db, patient_id, current_doctor)


@router.patch(
    "/{patient_id}",
    response_model=schemas.PatientResponse,
)
def update_patient(
    patient_id: int,
    patient_data: schemas.PatientUpdateRequest,
    db: Session = Depends(get_db),
    current_doctor: User = Depends(get_current_doctor),
):
    return service.update_patient(db, patient_id, patient_data, current_doctor)    