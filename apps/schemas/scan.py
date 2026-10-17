from datetime import datetime

# from typing import Optional
from apps.models.scan import ScanType
from pydantic import BaseModel, ConfigDict


class ScanCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    scan_type: ScanType
    timestamp: datetime


class ScanResponse(BaseModel):
    id: int
    user_id: int
    scan_type: ScanType
    timestamp: datetime
    model_config = ConfigDict(from_attributes=True)
