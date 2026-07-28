from io import BytesIO

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.dependencies import (
    get_current_doctor,
    get_db,
)
from app.reports import service
from app.users.models import User
from app.emails.dependencies import get_email_service
from app.emails.email_service import EmailService
from app.emails.providers import EmailDeliveryError
from app.patients.models import Patient



router = APIRouter(
    prefix=(
        "/patients/{patient_id}/assessments/"
        "{assessment_id}/report"
    ),
    tags=["Reports"],
)




@router.get("/view")
def view_assessment_report(
    patient_id: int,
    assessment_id: int,
    db: Session = Depends(get_db),
    current_doctor: User = Depends(
        get_current_doctor
    ),
):
    pdf = service.build_assessment_report(
        db=db,
        patient_id=patient_id,
        assessment_id=assessment_id,
        current_doctor=current_doctor,
    )

    return service.create_pdf_response(
        pdf=pdf,
        assessment_id=assessment_id,
        disposition="inline",
    )


@router.get("/download")
def download_assessment_report(
    patient_id: int,
    assessment_id: int,
    db: Session = Depends(get_db),
    current_doctor: User = Depends(
        get_current_doctor
    ),
):
    pdf = service.build_assessment_report(
        db=db,
        patient_id=patient_id,
        assessment_id=assessment_id,
        current_doctor=current_doctor,
    )

    return service.create_pdf_response(
        pdf=pdf,
        assessment_id=assessment_id,
        disposition="attachment",
    )
    
@router.post("/send-report")
async def send_assessment_report(
  patient_id: int,
  assesment_id: int,
  db: Session = Depends(get_db),
  current_doctor: User = Depends(get_current_doctor),
  EmailService: EmailService = Depends(get_email_service)  
):
    return await service.email_assessment_report(
        patient_id=patient_id,
        assessment_id=assesment_id,
        db=db,
        current_doctor=current_doctor,
        email_service=EmailService
    )
    
     