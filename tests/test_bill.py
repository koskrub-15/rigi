from httpx import AsyncClient

from apps.core.security import create_zone_token
from tests.conftest import MakeAuthClient


async def ride(
    client: AsyncClient,
    check_in: str,
    check_out: str,
    from_zone: str = "A",
    to_zone: str = "A",
):
    for scan_type, timestamp, zone in [
        ("check_in", check_in, from_zone),
        ("check_out", check_out, to_zone),
    ]:
        response = await client.post(
            "/scans",
            json={
                "scan_type": scan_type,
                "timestamp": timestamp,
                "code": create_zone_token(zone),
            },
        )
        assert response.status_code == 201


async def get_bill(client: AsyncClient, date_from: str, date_to: str):
    response = await client.get(
        "/bill",
        params={"date_from": date_from, "date_to": date_to},
    )
    assert response.status_code == 200
    return response.json()


async def test_three_trips_cost_nine(auth_client: AsyncClient):
    await ride(auth_client, "2026-10-13T08:00", "2026-10-13T08:30")
    await ride(auth_client, "2026-10-14T08:00", "2026-10-14T08:30")
    await ride(auth_client, "2026-10-15T18:00", "2026-10-15T18:40")

    bill = await get_bill(auth_client, "2026-10-01T00:00", "2026-11-01T00:00")

    assert bill["total"] == 9
    assert len(bill["tickets"]) == 3
    assert all(t["type"] == "single_ticket" for t in bill["tickets"])


async def test_trips_outside_period_are_not_billed(auth_client: AsyncClient):
    await ride(auth_client, "2026-09-20T08:00", "2026-09-20T08:30")
    await ride(auth_client, "2026-10-14T08:00", "2026-10-14T08:30")
    await ride(auth_client, "2026-11-05T08:00", "2026-11-05T08:30")

    bill = await get_bill(auth_client, "2026-10-01T00:00", "2026-11-01T00:00")

    assert bill["total"] == 3
    assert [t["valid_from"] for t in bill["tickets"]] == ["2026-10-14T08:00:00"]


async def test_other_users_trips_are_not_billed(
    auth_client: AsyncClient, make_auth_client: MakeAuthClient
):
    other_client = await make_auth_client("other@example.com")
    await ride(auth_client, "2026-10-14T08:00", "2026-10-14T08:30")
    await ride(other_client, "2026-10-14T09:00", "2026-10-14T09:30")

    bill = await get_bill(auth_client, "2026-10-01T00:00", "2026-11-01T00:00")

    assert bill["total"] == 3


async def test_period_with_timezone(auth_client: AsyncClient):
    # так время шлёт JS: new Date().toISOString() -> "...Z"
    await ride(auth_client, "2026-10-14T08:00", "2026-10-14T08:30")

    bill = await get_bill(auth_client, "2026-10-01T00:00Z", "2026-11-01T00:00Z")

    assert bill["total"] == 3


async def test_scan_with_offset_is_stored_in_utc(auth_client: AsyncClient):
    # 10:00 по Берлину (+02:00) — это 08:00 UTC
    await ride(auth_client, "2026-10-14T10:00+02:00", "2026-10-14T10:30+02:00")

    bill = await get_bill(auth_client, "2026-10-01T00:00", "2026-11-01T00:00")

    assert [t["valid_from"] for t in bill["tickets"]] == ["2026-10-14T08:00:00"]


async def test_single_price_depends_on_zones(auth_client: AsyncClient):
    # A -> B: 2 зоны, разовый 6 (дешевле дневного 8)
    await ride(auth_client, "2026-10-14T08:00", "2026-10-14T08:30", "A", "B")

    bill = await get_bill(auth_client, "2026-10-01T00:00", "2026-11-01T00:00")

    assert bill["tickets"] == [
        {"type": "single_ticket", "valid_from": "2026-10-14T08:00:00", "price": 6}
    ]


async def test_long_trip_gets_day_ticket(auth_client: AsyncClient):
    # A -> E: 3 зоны, разовый 9 > дневной 8 — дневной на всех зонах выгоднее
    await ride(auth_client, "2026-10-14T08:00", "2026-10-14T08:30", "A", "E")

    bill = await get_bill(auth_client, "2026-10-01T00:00", "2026-11-01T00:00")

    assert [t["type"] for t in bill["tickets"]] == ["day_ticket"]
    assert bill["total"] == 8
