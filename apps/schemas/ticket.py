from datetime import datetime
from pydantic import BaseModel, ConfigDict

from apps.core.enums import TicketType


class TicketResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    type: TicketType
    valid_from: datetime
    price: int
