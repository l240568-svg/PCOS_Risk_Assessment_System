from dataclasses import dataclass

@dataclass(frozen=True)
class EmailAttachment:
    filename: str
    content: bytes
    content_type: str = "application/octet-stream"

@dataclass(frozen=True)
class EmailMessage:
    to: list[str]
    subject: str
    from_email: str
    html:str
    text:str|None
    attachments: tuple[EmailAttachment, ...] = ()
    
    