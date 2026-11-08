from datetime import datetime
from apps.db.base import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import DateTime, UniqueConstraint, ForeignKey, JSON
from typing import Any


class BillModel(Base):
    __tablename__ = "bills"
    __table_args__ = (
        UniqueConstraint("user_id", "year", "month", name="uq_bills_user_period"),
    )
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    year: Mapped[int] = mapped_column()
    month: Mapped[int] = mapped_column()
    tickets: Mapped[list[dict[str, Any]]] = mapped_column(JSON)
    total: Mapped[int] = mapped_column()
    closed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
