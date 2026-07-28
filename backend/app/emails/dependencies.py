from fastapi import Depends

from app.core.config import Settings, get_settings
from app.emails.email_service import EmailService
from app.emails.factory import build_email_service


def get_email_service(settings: Settings = Depends(get_settings),) -> EmailService:
    return build_email_service(settings)