from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import (
    get_current_doctor,
    get_db,
)
from app.dashboard import schemas, service
from app.users.models import User


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


@router.get(
    "",
    response_model=schemas.DashboardResponse,
)
def get_dashboard(
    db: Session = Depends(get_db),
    current_doctor: User = Depends(
        get_current_doctor
    ),
):
    return service.get_dashboard(
        db=db,
        current_doctor=current_doctor,
    )