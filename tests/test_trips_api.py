from datetime import datetime, timedelta, timezone

import pytest
from httpx import AsyncClient

from apps.core.security import create_zone_token
from apps.core.tariffs import MAX_TRIP_DURATION
from apps.api.v1.endpoints import trips as trips_endpoint
from tests.test_bill import ride


@pytest.fixture
def freeze_trips_time(monkeypatch):
    now = datetime(2026, 10, 14, 12, tzinfo=timezone.utc)

    class FrozenDateTime(datetime):
        @classmethod
        def now(cls, tz=None):
            return now.astimezone(tz) if tz else now.replace(tzinfo=None)

    monkeypatch.setattr(trips_endpoint, "datetime", FrozenDateTime)
    return now.replace(tzinfo=None)


async def scan(auth_client: AsyncClient, scan_type: str, timestamp: str):
    return await auth_client.post(
        "/scans",
        json={
            "scan_type": scan_type,
            "timestamp": timestamp,
            "code": create_zone_token("B"),
        },
    )


async def test_current_trip_returns_null_without_scans(auth_client: AsyncClient):
    response = await auth_client.get("/trips/current")

    assert response.status_code == 200
    assert response.json() is None


async def test_current_trip_returns_recent_open_check_in(
    auth_client: AsyncClient, freeze_trips_time: datetime
):
    await scan(auth_client, "check_in", "2026-10-14T11:00")

    response = await auth_client.get("/trips/current")

    assert response.status_code == 200
    assert response.json() == {"start": "2026-10-14T11:00:00", "from_zone": "B"}


async def test_current_trip_returns_null_after_check_out(
    auth_client: AsyncClient, freeze_trips_time: datetime
):
    await scan(auth_client, "check_in", "2026-10-14T11:00")
    await scan(auth_client, "check_out", "2026-10-14T11:30")

    response = await auth_client.get("/trips/current")

    assert response.status_code == 200
    assert response.json() is None


async def test_current_trip_returns_null_for_check_in_older_than_max_duration(
    auth_client: AsyncClient, freeze_trips_time: datetime
):
    now = freeze_trips_time
    timestamp = now - MAX_TRIP_DURATION - timedelta(minutes=1)
    await scan(auth_client, "check_in", timestamp.isoformat())

    response = await auth_client.get("/trips/current")

    assert response.status_code == 200
    assert response.json() is None


async def test_current_trip_returns_null_at_max_duration_boundary(
    auth_client: AsyncClient, freeze_trips_time: datetime
):
    now = freeze_trips_time
    timestamp = now - MAX_TRIP_DURATION
    await scan(auth_client, "check_in", timestamp.isoformat())

    response = await auth_client.get("/trips/current")

    assert response.status_code == 200
    assert response.json() is None


async def test_current_trip_requires_authentication(client: AsyncClient):
    response = await client.get("/trips/current")

    assert response.status_code == 401


async def test_trips_without_date_range_returns_all_trips(auth_client: AsyncClient):
    await ride(auth_client, "2026-08-14T08:00", "2026-08-14T08:30")
    await ride(auth_client, "2026-09-14T08:00", "2026-09-14T08:30")
    await ride(auth_client, "2026-10-14T08:00", "2026-10-14T08:30")

    response = await auth_client.get("/trips")

    assert response.status_code == 200
    assert [trip["start"] for trip in response.json()] == [
        "2026-08-14T08:00:00",
        "2026-09-14T08:00:00",
        "2026-10-14T08:00:00",
    ]


async def test_trips_filters_scans_by_half_open_date_range(auth_client: AsyncClient):
    await ride(auth_client, "2026-10-13T08:00", "2026-10-13T08:30")
    await ride(auth_client, "2026-10-14T08:00", "2026-10-14T08:30")
    await ride(auth_client, "2026-10-15T08:00", "2026-10-15T08:30")

    response = await auth_client.get(
        "/trips",
        params={
            "date_from": "2026-10-14T08:00",
            "date_to": "2026-10-15T08:00",
        },
    )

    assert response.status_code == 200
    assert [trip["start"] for trip in response.json()] == ["2026-10-14T08:00:00"]


async def test_trips_normalizes_date_range_to_utc(auth_client: AsyncClient):
    await ride(auth_client, "2026-10-14T08:30", "2026-10-14T08:45")

    response = await auth_client.get(
        "/trips",
        params={
            "date_from": "2026-10-14T10:00+02:00",
            "date_to": "2026-10-14T11:00+02:00",
        },
    )

    assert response.status_code == 200
    assert [trip["start"] for trip in response.json()] == ["2026-10-14T08:30:00"]


async def test_trips_rejects_reversed_date_range(auth_client: AsyncClient):
    response = await auth_client.get(
        "/trips",
        params={
            "date_from": "2026-10-15T00:00",
            "date_to": "2026-10-14T00:00",
        },
    )

    assert response.status_code == 422


@pytest.mark.parametrize(
    "params",
    [
        {"date_from": "2026-10-14T00:00"},
        {"date_to": "2026-10-15T00:00"},
    ],
)
async def test_trips_rejects_range_with_only_one_bound(
    auth_client: AsyncClient, params: dict[str, str]
):
    response = await auth_client.get(
        "/trips",
        params=params,
    )

    assert response.status_code == 422
