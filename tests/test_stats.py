from httpx import AsyncClient

from apps.core.tariffs import currency
from tests.test_bill import get_bill, ride

OCTOBER = ("2026-10-01T00:00", "2026-11-01T00:00")


async def get_stats(client: AsyncClient, date_from: str, date_to: str):
    response = await client.get(
        "/stats",
        params={"date_from": date_from, "date_to": date_to},
    )
    assert response.status_code == 200
    return response.json()


async def test_three_trips_in_two_days(auth_client: AsyncClient):
    await ride(auth_client, "2026-10-13T08:00", "2026-10-13T08:30")
    await ride(auth_client, "2026-10-13T18:00", "2026-10-13T18:30")
    await ride(auth_client, "2026-10-14T08:00", "2026-10-14T08:30")

    stats = await get_stats(auth_client, *OCTOBER)

    assert stats["trips_count"] == 3
    assert stats["singles_price"] == 9
    assert stats["paid"] == 9
    assert stats["per_day"] == [
        {"day": "2026-10-13", "trips": 2},
        {"day": "2026-10-14", "trips": 1},
    ]


async def test_empty_period(auth_client: AsyncClient):
    await ride(auth_client, "2026-09-20T08:00", "2026-09-20T08:30")

    stats = await get_stats(auth_client, *OCTOBER)

    assert stats == {
        "trips_count": 0,
        "paid": 0,
        "singles_price": 0,
        "per_day": [],
        "currency": currency,
    }


async def test_paid_equals_bill_total(auth_client: AsyncClient):
    # 4 поездки в один день: дневной (8) дешевле разовых (12)
    for hour in ["07", "10", "13", "16"]:
        await ride(auth_client, f"2026-10-14T{hour}:00", f"2026-10-14T{hour}:30")
    await ride(auth_client, "2026-10-20T08:00", "2026-10-20T08:30")

    stats = await get_stats(auth_client, *OCTOBER)
    bill = await get_bill(auth_client, *OCTOBER)

    assert stats["paid"] == bill["total"] == 11
    assert stats["singles_price"] == 15


async def test_singles_price_counts_zones(auth_client: AsyncClient):
    # A -> B (2 зоны) и B -> F (3 зоны) в разные дни: разовыми 6 + 9 = 15,
    # оптимально 6 + 8 (дневной на длинную)
    await ride(auth_client, "2026-10-13T08:00", "2026-10-13T08:30", "A", "B")
    await ride(auth_client, "2026-10-14T08:00", "2026-10-14T08:30", "B", "F")

    stats = await get_stats(auth_client, *OCTOBER)

    assert stats["singles_price"] == 15
    assert stats["paid"] == 14


async def test_paid_across_september_and_october(auth_client: AsyncClient):
    for day in range(28, 31):
        for hour in ("08", "18"):
            await ride(
                auth_client,
                f"2026-09-{day:02d}T{hour}:00",
                f"2026-09-{day:02d}T{hour}:30",
            )
    for day in range(1, 5):
        for hour in ("08", "18"):
            await ride(
                auth_client,
                f"2026-10-{day:02d}T{hour}:00",
                f"2026-10-{day:02d}T{hour}:30",
            )

    stats = await get_stats(
        auth_client,
        "2026-09-28T00:00",
        "2026-10-05T00:00",
    )

    assert stats["paid"] == 42


async def test_reversed_period_returns_unprocessable_entity(auth_client: AsyncClient):
    response = await auth_client.get(
        "/stats",
        params={
            "date_from": "2026-10-05T00:00",
            "date_to": "2026-09-28T00:00",
        },
    )

    assert response.status_code == 422
