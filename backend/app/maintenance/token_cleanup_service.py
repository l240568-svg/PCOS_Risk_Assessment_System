from dataclasses import dataclass

from sqlalchemy import  delete, func
from app.auth.models import RefreshToken, RevokedToken
from sqlalchemy.orm import Session


@dataclass(frozen=True)
class TokenCleanupResult:
    revoked_tokens_deleted: int
    refresh_tokens_deleted: int


def cleanup_expired_tokens(db: Session) -> TokenCleanupResult:
    """Atomically delete authentication tokens that have expired."""

    try:
        revoked_result = db.execute(
            delete(RevokedToken).where(
                RevokedToken.expires_at <= func.now()
            )
        )

        refresh_result = db.execute(
            delete(RefreshToken).where(
                RefreshToken.expires_at <= func.now()
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