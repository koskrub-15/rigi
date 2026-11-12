from apps.db.session import get_db
from apps.schemas.stats import StatsResponse
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from apps.services.optimizer import get_price_of_single_ticket, optimizer, total_price
from datetime import datetime, timezone
from apps.services.trips import get_trips, trips_per_day
from apps.models.user import User
from apps.api.deps import get_current_user
from apps.services.month import split_by_months
from apps.core.datetimes import to_naive_utc


stats_router = APIRouter(prefix="/stats", tags=["stats"])


@stats_router.get("", response_model=StatsResponse)
async def get_stats_endpoint(
    date_from: datetime,
    date_to: datetime,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> StatsResponse:
    """Get users stats"""
    date_from, date_to = to_naive_utc(date_from), to_naive_utc(date_to)

    if date_to <= date_from:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="date_from must be earlier than date_to",
        )

    all_trips = await get_trips(
        user_id=current_user.id,
        date_from=date_from,
        date_to=date_to,
        now=datetime.now(timezone.utc),
        db=db,
    )

    total_tickets = []
    for start, end in split_by_months(date_from, date_to):
        start, end = to_naive_utc(start), to_naive_utc(end)
        tickets = optimizer(
            trips=[trip for trip in all_trips if start <= trip.start < end]
        )
        total_tickets.extend(tickets)
    total = total_price(total_tickets)
    singles_price = sum(get_price_of_single_ticket(trip=trip) for trip in all_trips)
    per_day = trips_per_day(trips=all_trips)
    return StatsResponse(
        trips_count=len(all_trips),
        paid=total,
        singles_price=singles_price,
        per_day=per_day,
    )
