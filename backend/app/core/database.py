from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import get_settings


settings = get_settings()


class Base(DeclarativeBase):  #without "base" sqlalchemy will not know which classes are database models
    pass


engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  #opens a fresh connection automatically
)


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)