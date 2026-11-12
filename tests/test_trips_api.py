import pytest
from httpx import AsyncClient

from tests.test_bill import ride


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
