from abc import ABC, abstractmethod
from app.emails.EmailModel import EmailMessage
from app.emails.providers import EmailProvider, SMTPEmailProvider, ResendEmailProvider
from app.emails.email_service import EmailService

#<<Factory interface>>
class EmailProviderFactory(ABC):
    def __init__(self, settings): 
        self.settings = settings
    
    @abstractmethod
    def create_provider(self) -> EmailProvider:
        pass
    
    def create_email_service(self)->"EmailService":
        provider = self.create_provider()
        return EmailService(provider)   
    
    
    
#Concrete factories for Gmail and Resend email providers
    
class MailtrapEmailFactory(EmailProviderFactory):
    def create_provider(self) -> EmailProvider:
        return SMTPEmailProvider(
            host=self.settings.MAILTRAP_HOST,
            port=self.settings.MAILTRAP_PORT,
            username=self.settings.MAILTRAP_USERNAME,
            password=self.settings.MAILTRAP_PASSWORD,
            from_email=self.settings.MAIL_FROM
        )

class GmailEmailFactory(EmailProviderFactory):
    def create_provider(self) -> EmailProvider:
        return SMTPEmailProvider(
            host=self.settings.SMTP_SERVER,
            port=self.settings.GMAIL_PORT,
            username=self.settings.GMAIL_APP,
            password=self.settings.GMAIL_APP_PASSWORD,
            from_email=self.settings.GMAIL_FROM,
        )

class ResendEmailFactory(EmailProviderFactory):
    def create_provider(self) -> EmailProvider:
        return ResendEmailProvider(
            api_key=self.settings.RESEND_API_KEY,
            from_email=self.settings.RESEND_FROM,
        )
        
        
EMAIL_FACTORIES: dict[ str, type[EmailProviderFactory]] = {
    "mailtrap": MailtrapEmailFactory,
    "gmail": GmailEmailFactory,
    "resend": ResendEmailFactory,
}


def build_email_service(settings) -> EmailService:
    provider_name = settings.EMAIL_PROVIDER.lower()

    factory_class = EMAIL_FACTORIES.get(provider_name)

    if factory_class is None:
        raise RuntimeError(
            f"Unsupported email provider: {provider_name}"
        )

    factory = factory_class(settings)

    return factory.create_email_service()