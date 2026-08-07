from dataclasses import dataclass

from sqlalchemy import Column, DateTime, MetaData, Table, delete, func
from sqlalchemy.orm import Session


metadata = MetaData()

revoked_tokens = Table(
    "revoked_tokens",
    metadata,
    Column("expires_at", DateTime(timezone=True), nullable=False),
    schema="public",
)

refresh_tokens = Table(
    "refresh_tokens",
    metadata,
    Column("expires_at", DateTime(timezone=True), nullable=False),
    schema="public",
)


@dataclass(frozen=True)
class TokenCleanupResult:
    revoked_tokens_deleted: int
    refresh_tokens_deleted: int


def cleanup_expired_tokens(db: Session) -> TokenCleanupResult:
    try:
        revoked_result = db.execute(
            delete(revoked_tokens).where(
                revoked_tokens.c.expires_at <= func.now()
            )
        )

        refresh_result = db.execute(
            delete(refresh_tokens).where(
                refresh_tokens.c.expires_at <= func.now()
            )
        )

        db.commit()

        return TokenCleanupResult(
            revoked_tokens_deleted=revoked_result.rowcount or 0,
            refresh_tokens_deleted=refresh_result.rowcount or 0,
        )
    except Exception:
        db.rollback()
        raise