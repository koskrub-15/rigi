from datetime import datetime

from apps.db.session import get_db
from apps.schemas.bill import BillResponse
from apps.services.trips import get_trips
from apps.services.optimizer import optimizer, total_price
from fastapi import APIRouter, Depends

from sqlalchemy.ext.asyncio import AsyncSession


bill_router = APIRouter(prefix="/bill", tags=["bill"])


@bill_router.get("", response_model=BillResponse)
async def create_bill(
    user_id: int,
    date_from: datetime,
    date_to: datetime,
    db: AsyncSession = Depends(get_db),
) -> BillResponse:
    """Create a month bill"""
    trips = await get_trips(
        user_id=user_id, date_from=date_from, date_to=date_to, db=db
    )
    tickets = optimizer(trips=trips)
    return BillResponse(tickets=tickets, total=total_price(tickets))
