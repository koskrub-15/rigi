from datetime import datetime

# from typing import Optional
from apps.core.datetimes import to_naive_utc
from apps.core.enums import ScanType
from pydantic import BaseModel, ConfigDict, field_validator


class ScanCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    scan_type: ScanType
    timestamp: datetime

    @field_validator("timestamp")
    @classmethod
    def timestamp_to_utc(cls, value: datetime) -> datetime:
        return to_naive_utc(value)


class ScanResponse(BaseModel):
    id: int
    user_id: int
    scan_type: ScanType
    timestamp: datetime
    model_config = ConfigDict(from_attributes=True)
