from datetime import datetime

# from typing import Optional
from apps.core.datetimes import to_naive_utc
from apps.core.enums import ScanType
from pydantic import BaseModel, ConfigDict, field_validator


from apps.core.zones import Zone


class ScanCreate(BaseModel):
    """Incoming scan from a validator device."""

    scan_type: ScanType
    timestamp: datetime
    zone: Zone

    @field_validator("timestamp")
    @classmethod
    def timestamp_to_utc(cls, value: datetime) -> datetime:
        """Normalize the timestamp to naive UTC."""
        return to_naive_utc(value)


class ScanResponse(BaseModel):
    id: int
    user_id: int
    scan_type: ScanType
    timestamp: datetime
    zone: str
    model_config = ConfigDict(from_attributes=True)
