from datetime import datetime

from apps.core.datetimes import to_naive_utc
from apps.db.session import get_db
from apps.schemas.bill import BillResponse
from apps.services.optimizer import total_price, optimizer
from fastapi import APIRouter, Depends

from apps.CRUD.scan import get_scans
from sqlalchemy.ext.asyncio import AsyncSession
from apps.services.trips import build_trips

bill_router = APIRouter(prefix="/bill", tags=["bill"])


@bill_router.get("", response_model=BillResponse)
async def create_bill(
    user_id: int,
    date_from: datetime,
    date_to: datetime,
    db: AsyncSession = Depends(get_db),
) -> BillResponse:
    """Create a month bill"""
    date_from, date_to = to_naive_utc(date_from), to_naive_utc(date_to)
    trips = build_trips(scans=await get_scans(db=db, user_id=user_id))
    trips = [trip for trip in trips if date_from <= trip.start < date_to]
    tickets = optimizer(trips)
    return BillResponse(tickets=tickets, total=total_price(tickets))
