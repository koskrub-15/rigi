from datetime import datetime
from pydantic import BaseModel, ConfigDict

from apps.schemas.ticket import TicketResponse
from apps.core.tariffs import currency


class BillResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    tickets: list[TicketResponse]
    total: int
    currency: str = currency


class ClosedBillResponse(BillResponse):
    id: int
    year: int
    month: int
    closed_at: datetime
    paid_at: datetime | None


class PaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    url: str
