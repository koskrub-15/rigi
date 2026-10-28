from datetime import datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from apps.models.revoked_token import RevokedToken


async def revoke(db: AsyncSession, jti: str, expires_at: datetime) -> bool:
    """Revoke a token by its jti; False if it was already revoked.

    The unique index on jti makes this atomic under concurrent requests.
    """
    db.add(RevokedToken(jti=jti, expires_at=expires_at))
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        return False
    return True
