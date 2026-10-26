from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from apps.core.zones import Zone


class TripResponse(BaseModel):
    """Trip between two tariff zones."""

    model_config = ConfigDict(from_attributes=True)

    start: datetime
    end: datetime
    from_zone: Zone
    to_zone: Zone
    zones: int = Field(ge=1)
