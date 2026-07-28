from app.emails.providers import EmailProvider
from app.emails.EmailModel import EmailMessage
from app.emails.templates import otp_template_html

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
