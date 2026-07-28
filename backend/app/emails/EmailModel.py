from dataclasses import dataclass

@dataclass(frozen=True)
class EmailMessage:
    to: list[str]
    subject: str
    from_email: str
    html:str
    text:str|None
    