from datetime import datetime, timezone
from typing import Annotated
from apps.db.session import get_db
from apps.schemas.trip import TripResponse
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from apps.services.trips import get_trips
from apps.models.user import User
from apps.api.deps import get_current_user
from apps.core.datetimes import to_naive_utc


trip_router = APIRouter(prefix="/trips", tags=["trips"])


@trip_router.get("", response_model=list[TripResponse])
async def build_trips_endpoint(
    date_from: Annotated[datetime | None, Query()] = None,
    date_to: Annotated[datetime | None, Query()] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[TripResponse]:
    """Return the current user's trips, optionally within ``[date_from, date_to)``.

    Both bounds must be given together or omitted together.
    """
    if (date_from is None) != (date_to is None):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="date_from and date_to must be provided together",
        )

    if date_from is not None and date_to is not None:
        date_from, date_to = to_naive_utc(date_from), to_naive_utc(date_to)
        if date_to <= date_from:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="date_from must be earlier than date_to",
            )

    trips = await get_trips(
        db=db,
        user_id=current_user.id,
        date_from=date_from,
        date_to=date_to,
        now=datetime.now(timezone.utc),
    )
    return trips
