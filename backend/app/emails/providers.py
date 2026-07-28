import asyncio
import smtplib
import ssl
import base64
from abc import ABC, abstractmethod
from email.message import EmailMessage as MIMEEmailMessage
from email.utils import make_msgid

import resend

from app.emails.EmailModel import EmailMessage

class EmailDeliveryError(RuntimeError):
    """Raised when an email provider fails to send an email."""

# <<Strategy interface>>
class EmailProvider(ABC):
    @abstractmethod
    async def send(self, email_message: EmailMessage) -> None:
        pass
    
class SMTPEmailProvider(EmailProvider): 
    def __init__(
        self,
        host:str,
        port:int,
        username:str,
        password:str,
        from_email:str
    ):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.from_email = from_email
        
    async def send(self, message:EmailMessage)->str:
        return await asyncio.to_thread(self._send_email_sync, message)
    
    def _send_email_sync(self, email_message: EmailMessage) -> str:
        mime_message = MIMEEmailMessage()
        message_id = make_msgid()

        mime_message["Message-ID"] = message_id
        mime_message["From"] = email_message.from_email
        mime_message["To"] = ", ".join(email_message.to)
        mime_message["Subject"] = email_message.subject

        # Plain-text fallback
        mime_message.set_content(
            email_message.text
        )

        # HTML version
        mime_message.add_alternative(
            email_message.html,
            subtype="html",
        )
        
        for attachment in email_message.attachments:
         maintype, subtype = attachment.content_type.split("/", 1)

         mime_message.add_attachment(
         attachment.content,
         maintype=maintype,
         subtype=subtype,
         filename=attachment.filename,
    )

        tls_context = ssl.create_default_context()

        try:
            with smtplib.SMTP(
                host=self.host,
                port=self.port,
                timeout=15,
            ) as smtp:
                smtp.ehlo()
                smtp.starttls(context=tls_context)
                smtp.ehlo()

                smtp.login(
                    self.username,
                    self.password,
                )

                refused_recipients = smtp.send_message(
                    mime_message
                )

        except (smtplib.SMTPException, OSError) as exc:
            raise EmailDeliveryError(
                f"SMTP email delivery failed: {exc}"
            ) from exc

        if refused_recipients:
            refused = ", ".join(refused_recipients.keys())

            raise EmailDeliveryError(
                f"SMTP server refused these recipients: {refused}"
            )

        return message_id

        


class ResendEmailProvider(EmailProvider):
    def __init__(
        self,
        api_key:str,
        from_email:str
    ):
        self.api_key = api_key
        self.from_email = from_email
        
    async def send(self,message: EmailMessage) -> str | None:
     return await asyncio.to_thread(
        self._send_email_sync,
        message,
    )
    def _send_email_sync( self,email_message: EmailMessage) -> str | None:
        resend.api_key = self.api_key

        params: resend.Emails.SendParams = {
            "from": email_message.from_email,
            "to": email_message.to,
            "subject": email_message.subject,
        }
        
        if email_message.html:
            params["html"] = email_message.html

        if email_message.text:
            params["text"] = email_message.text
            
        if email_message.attachments:
           params["attachments"] = [
         {
            "filename": attachment.filename,
            "content": base64.b64encode(
                attachment.content
            ).decode("ascii"),
        }
           for attachment in email_message.attachments
           ]

        try:
            response = resend.Emails.send(params)
        except Exception as exc:
            raise EmailDeliveryError(
                f"Resend email delivery failed: {exc}"
            ) from exc

        if isinstance(response, dict):
            return response.get("id")

        return getattr(response, "id", None)