from apps.db.session import get_db
from apps.schemas.stats import StatsResponse
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from apps.services.optimizer import get_price_of_single_ticket, optimizer, total_price
from datetime import datetime, timezone
from apps.services.trips import get_trips, trips_per_day
from apps.models.user import User
from apps.api.deps import get_current_user


stats_router = APIRouter(prefix="/stats", tags=["stats"])


@stats_router.get("", response_model=StatsResponse)
async def get_stats_endpoint(
    date_from: datetime,
    date_to: datetime,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> StatsResponse:
    """Get users stats"""
    trips = await get_trips(
        user_id=current_user.id,
        date_from=date_from,
        date_to=date_to,
        now=datetime.now(timezone.utc),
        db=db,
    )
    tickets = optimizer(trips=trips)
    total = total_price(tickets)
    singles_price = sum(get_price_of_single_ticket(trip=trip) for trip in trips)
    per_day = trips_per_day(trips=trips)
    return StatsResponse(
        trips_count=len(trips), paid=total, singles_price=singles_price, per_day=per_day
    )
