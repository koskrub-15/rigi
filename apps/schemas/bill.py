from pydantic import BaseModel, ConfigDict

from apps.schemas.ticket import TicketResponse


class BillResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    tickets: list[TicketResponse]
    total: int
