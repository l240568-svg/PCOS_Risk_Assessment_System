from io import BytesIO

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.dependencies import (
    get_current_doctor,
    get_db,
)
from app.reports import service
from app.users.models import User


router = APIRouter(
    prefix=(
        "/patients/{patient_id}/assessments/"
        "{assessment_id}/report"
    ),
    tags=["Reports"],
)


def create_pdf_response(
    pdf: BytesIO,
    assessment_id: int,
    disposition: str,
) -> StreamingResponse:
    filename = (
        f"pcos-assessment-{assessment_id}.pdf"
    )

    return StreamingResponse(
        pdf,
        media_type="application/pdf",
        headers={
            "Content-Disposition": (
                f'{disposition}; filename="{filename}"'
            ),
            "Content-Length": str(
                pdf.getbuffer().nbytes
            ),
            "Cache-Control": "no-store",
        },
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

    return create_pdf_response(
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

    return create_pdf_response(
        pdf=pdf,
        assessment_id=assessment_id,
        disposition="attachment",
    )