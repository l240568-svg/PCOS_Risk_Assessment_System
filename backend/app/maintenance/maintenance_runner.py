import os

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import NullPool

from app.maintenance.token_cleanup_service import cleanup_expired_tokens


def normalize_database_url(url: str) -> str:
    if url.startswith("postgres://"):
        return url.replace(
            "postgres://",
            "postgresql+psycopg2://",
            1,
        )

    if url.startswith("postgresql://"):
        return url.replace(
            "postgresql://",
            "postgresql+psycopg2://",
            1,
        )

    return url


def main() -> None:
    database_url = os.environ.get("RENDER_DATABASE_URL")

    if not database_url:
        raise RuntimeError("RENDER_DATABASE_URL is not configured")

    engine = create_engine(
        normalize_database_url(database_url),
        pool_pre_ping=True,
        poolclass=NullPool,
        connect_args={"sslmode": "require"},
    )

    try:
        with Session(engine) as db:
            result = cleanup_expired_tokens(db)

        print(
            "Token cleanup completed: "
            f"revoked_tokens={result.revoked_tokens_deleted}, "
            f"refresh_tokens={result.refresh_tokens_deleted}"
        )
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()