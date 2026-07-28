from io import BytesIO

from app.emails.providers import EmailProvider
from app.emails.EmailModel import EmailMessage, EmailAttachment
from app.emails.templates import assessment_template_html, otp_template_html
from app.emails.EmailModel import (
    EmailAttachment,
    EmailMessage,
)

class EmailService:
    def __init__(self, provider: EmailProvider):
        self.provider = provider

    async def send_otp_email(self, recipient_email: str, otp: str) -> None:
        message = EmailMessage(
            to=[recipient_email],
            subject="Your OTP Code",
            from_email=self.provider.from_email,
            html=otp_template_html(otp=otp),
            text=f"Your password reset OTP code is: {otp} \n Please do not share this code with anyone."
        )
        await self.provider.send(message)
        
    async def send_assessment_email(self,
      recipient_email: str,
      patient_name: str,
      doctor_name: str,
      assessment_id: int,
      pdf_content: bytes,) -> None:
        message = EmailMessage(
            to=[recipient_email],
            subject=f"{patient_name} - PCOS Assessment Report",
            from_email=self.provider.from_email,
            html=assessment_template_html(patient_name=patient_name, doctor_name=doctor_name),
            text=(
            f"Hello {patient_name},\n\n"
            f"Your PCOS assessment report prepared by "
            f"{doctor_name} is attached to this email."
        ),
            attachments=[EmailAttachment(filename=f"{patient_name}-PCOS_Assessment.pdf", content=pdf_content, content_type="application/pdf")],
        )
        await self.provider.send(message)
