from functools import lru_cache    #so that the settings object is created only once and reused
from pathlib import Path
from urllib.parse import quote_plus   #for safer password and username

from pydantic_settings import BaseSettings, SettingsConfigDict


ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


class Settings(BaseSettings):
    APP_NAME: str = "PCOS Risk Assessment API"
    ENVIRONMENT: str = "development"

    DB_DRIVER: str = "postgresql+psycopg2"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def DATABASE_URL(self) -> str:
        username = quote_plus(self.DB_USER)
        password = quote_plus(self.DB_PASSWORD)   #for safer password and username

        return (
            f"{self.DB_DRIVER}://{username}:{password}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )


# save the settings object in cache so that it is created only once and reused
#SINGLETON DESGIN PATTERN   
@lru_cache
def get_settings() -> Settings:
    return Settings()