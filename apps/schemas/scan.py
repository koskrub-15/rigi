from datetime import datetime
from apps.core.datetimes import to_naive_utc
from apps.core.enums import ScanType
from pydantic import BaseModel, ConfigDict, field_validator, AfterValidator, Field

from typing import Annotated

from apps.core.security import decode_zone_token


def check_zone_code(value: str) -> str:
    """Decode a signed zone code and return the zone it points to."""
    zone = decode_zone_token(value)
    if zone is None:
        raise ValueError("invalid zone code")
    return zone


ZoneCode = Annotated[str, AfterValidator(check_zone_code)]


class ScanCreate(BaseModel):
    """Incoming scan from a validator device."""

    scan_type: ScanType
    timestamp: datetime
    zone: ZoneCode = Field(validation_alias="code")

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
