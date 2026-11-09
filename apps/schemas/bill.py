from datetime import datetime
from pydantic import BaseModel, ConfigDict

from apps.schemas.ticket import TicketResponse


class BillResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    tickets: list[TicketResponse]
    total: int


class ClosedBillResponse(BillResponse):
    id: int
    year: int
    month: int
    closed_at: datetime
    paid_at: datetime | None


class PaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    url: str
