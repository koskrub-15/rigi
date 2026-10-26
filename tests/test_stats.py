from httpx import AsyncClient

from tests.test_bill import get_bill, ride

OCTOBER = ("2026-10-01T00:00", "2026-11-01T00:00")


async def get_stats(client: AsyncClient, user_id: int, date_from: str, date_to: str):
    response = await client.get(
        f"/users/{user_id}/stats",
        params={"date_from": date_from, "date_to": date_to},
    )
    assert response.status_code == 200
    return response.json()


async def test_three_trips_in_two_days(client: AsyncClient):
    await ride(client, 1, "2026-10-13T08:00", "2026-10-13T08:30")
    await ride(client, 1, "2026-10-13T18:00", "2026-10-13T18:30")
    await ride(client, 1, "2026-10-14T08:00", "2026-10-14T08:30")

    stats = await get_stats(client, 1, *OCTOBER)

    assert stats["trips_count"] == 3
    assert stats["singles_price"] == 9
    assert stats["paid"] == 9
    assert stats["per_day"] == [
        {"day": "2026-10-13", "trips": 2},
        {"day": "2026-10-14", "trips": 1},
    ]


async def test_empty_period(client: AsyncClient):
    await ride(client, 1, "2026-09-20T08:00", "2026-09-20T08:30")

    stats = await get_stats(client, 1, *OCTOBER)

    assert stats == {"trips_count": 0, "paid": 0, "singles_price": 0, "per_day": []}


async def test_paid_equals_bill_total(client: AsyncClient):
    # 4 поездки в один день: дневной (8) дешевле разовых (12)
    for hour in ["07", "10", "13", "16"]:
        await ride(client, 1, f"2026-10-14T{hour}:00", f"2026-10-14T{hour}:30")
    await ride(client, 1, "2026-10-20T08:00", "2026-10-20T08:30")

    stats = await get_stats(client, 1, *OCTOBER)
    bill = await get_bill(client, 1, *OCTOBER)

    assert stats["paid"] == bill["total"] == 11
    assert stats["singles_price"] == 15


async def test_singles_price_counts_zones(client: AsyncClient):
    # A -> B (2 зоны) и B -> F (3 зоны) в разные дни: разовыми 6 + 9 = 15,
    # оптимально 6 + 8 (дневной на длинную)
    await ride(client, 1, "2026-10-13T08:00", "2026-10-13T08:30", "A", "B")
    await ride(client, 1, "2026-10-14T08:00", "2026-10-14T08:30", "B", "F")

    stats = await get_stats(client, 1, *OCTOBER)

    assert stats["singles_price"] == 15
    assert stats["paid"] == 14
