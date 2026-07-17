from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import get_settings

import secrets

settings = get_settings()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_value(string: str) -> str:
    return pwd_context.hash(string)


def verify_hash(plain_text: str, hash: str) -> bool:
    return pwd_context.verify(plain_text, hash)


def create_access_token(data: dict) -> str:
    expire_time = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = data.copy()
    payload.update({"exp": expire_time})

    token = jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )

    return token


def decode_access_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        return payload
    except JWTError:
        return None
    
def validate_password_strength(password: str) -> None:

    if len(password.encode("utf-8")) > 72:
        raise ValueError("Password cannot be longer than 72 bytes")
    
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long")

    if not any(character.isupper() for character in password):
        raise ValueError("Password must contain at least one uppercase letter")

    if not any(character.islower() for character in password):
        raise ValueError("Password must contain at least one lowercase letter")

    special_characters = "!@#$%^&*()-_=+[]{}|;:'\",.<>?/`~"

    if not any(character in special_characters for character in password):
        raise ValueError("Password must contain at least one special character")    
        
    
#OTP 
def generate_OTP() -> str:
    #Generate a 6-digit OTP code
    return f"{secrets.randbelow(1000000):06d}"

def otp_expiration_time(minutes: int = 5) -> datetime:
    return datetime.now(timezone.utc) + timedelta(minutes=minutes)
