from datetime import datetime, timezone

from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.models.user import User
from apps.services.trips import get_trips
from tests.test_bill import ride


async def test_get_trips_keeps_trip_crossing_range_end(
    auth_client: AsyncClient, db_session: AsyncSession
):
    await ride(auth_client, "2026-10-14T23:30", "2026-10-15T00:30")
    user = await db_session.scalar(select(User).where(User.email == "user@example.com"))
    assert user is not None

    trips = await get_trips(
        user_id=user.id,
        now=datetime(2026, 10, 16, tzinfo=timezone.utc),
        db=db_session,
        date_from=datetime(2026, 10, 14),
        date_to=datetime(2026, 10, 15),
    )

    assert len(trips) == 1
    assert trips[0].start == datetime(2026, 10, 14, 23, 30)
    assert trips[0].end == datetime(2026, 10, 15, 0, 30)
