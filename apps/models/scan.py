from datetime import datetime
from apps.core.enums import ScanType
from apps.db.base import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import DateTime, String


class ScanModel(Base):
    __tablename__ = "scans"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime)
    scan_type: Mapped[ScanType] = mapped_column(String(20))
    zone: Mapped[str] = mapped_column(String(20))
