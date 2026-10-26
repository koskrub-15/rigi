from httpx import AsyncClient


async def ride(
    client: AsyncClient,
    user_id: int,
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
            f"/users/{user_id}/scans",
            json={"scan_type": scan_type, "timestamp": timestamp, "zone": zone},
        )
        assert response.status_code == 201


async def get_bill(client: AsyncClient, user_id: int, date_from: str, date_to: str):
    response = await client.get(
        f"/users/{user_id}/bill",
        params={"date_from": date_from, "date_to": date_to},
    )
    assert response.status_code == 200
    return response.json()


async def test_three_trips_cost_nine(client: AsyncClient):
    await ride(client, 1, "2026-10-13T08:00", "2026-10-13T08:30")
    await ride(client, 1, "2026-10-14T08:00", "2026-10-14T08:30")
    await ride(client, 1, "2026-10-15T18:00", "2026-10-15T18:40")

    bill = await get_bill(client, 1, "2026-10-01T00:00", "2026-11-01T00:00")

    assert bill["total"] == 9
    assert len(bill["tickets"]) == 3
    assert all(t["type"] == "single_ticket" for t in bill["tickets"])


async def test_trips_outside_period_are_not_billed(client: AsyncClient):
    await ride(client, 1, "2026-09-20T08:00", "2026-09-20T08:30")
    await ride(client, 1, "2026-10-14T08:00", "2026-10-14T08:30")
    await ride(client, 1, "2026-11-05T08:00", "2026-11-05T08:30")

    bill = await get_bill(client, 1, "2026-10-01T00:00", "2026-11-01T00:00")

    assert bill["total"] == 3
    assert [t["valid_from"] for t in bill["tickets"]] == ["2026-10-14T08:00:00"]


async def test_other_users_trips_are_not_billed(client: AsyncClient):
    await ride(client, 1, "2026-10-14T08:00", "2026-10-14T08:30")
    await ride(client, 2, "2026-10-14T09:00", "2026-10-14T09:30")

    bill = await get_bill(client, 1, "2026-10-01T00:00", "2026-11-01T00:00")

    assert bill["total"] == 3


async def test_period_with_timezone(client: AsyncClient):
    # так время шлёт JS: new Date().toISOString() -> "...Z"
    await ride(client, 1, "2026-10-14T08:00", "2026-10-14T08:30")

    bill = await get_bill(client, 1, "2026-10-01T00:00Z", "2026-11-01T00:00Z")

    assert bill["total"] == 3


async def test_scan_with_offset_is_stored_in_utc(client: AsyncClient):
    # 10:00 по Берлину (+02:00) — это 08:00 UTC
    await ride(client, 1, "2026-10-14T10:00+02:00", "2026-10-14T10:30+02:00")

    bill = await get_bill(client, 1, "2026-10-01T00:00", "2026-11-01T00:00")

    assert [t["valid_from"] for t in bill["tickets"]] == ["2026-10-14T08:00:00"]


async def test_unknown_zone_is_rejected(client: AsyncClient):
    response = await client.post(
        "/users/1/scans",
        json={"scan_type": "check_in", "timestamp": "2026-10-14T08:00", "zone": "Z"},
    )

    assert response.status_code == 422
