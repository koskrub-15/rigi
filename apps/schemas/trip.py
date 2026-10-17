from datetime import datetime

# from typing import Optional
from pydantic import BaseModel, ConfigDict


class TripResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    start: datetime
    end: datetime
