from datetime import datetime
from apps.db.base import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import DateTime, String


class RevokedToken(Base):
    __tablename__ = "revoked_tokens"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    jti: Mapped[str] = mapped_column(String(36), unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    def __repr__(self) -> str:
        return f"<RevokedToken(jti={self.jti}, expires_at={self.expires_at})>"
