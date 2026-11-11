from datetime import datetime, timezone

from httpx import AsyncClient
import pytest

from apps.api.v1.endpoints import bills as bills_endpoint
from apps.core.tariffs import currency
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
        "/bills/preview",
        params={"date_from": date_from, "date_to": date_to},
    )
    assert response.status_code == 200
    return response.json()


async def close_bill(client: AsyncClient, year: int, month: int):
    return await client.post(f"/bills/{year}/{month}")


def freeze_bill_time(monkeypatch: pytest.MonkeyPatch, instant: datetime) -> None:
    class FrozenDateTime(datetime):
        @classmethod
        def now(cls, tz=None):
            if tz is None:
                return instant.replace(tzinfo=None)
            return instant.astimezone(tz)

    monkeypatch.setattr(bills_endpoint, "datetime", FrozenDateTime)


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


async def test_preview_does_not_create_a_closed_bill(auth_client: AsyncClient):
    await ride(auth_client, "2026-10-14T08:00", "2026-10-14T08:30")

    preview = await get_bill(auth_client, "2026-10-01T00:00", "2026-11-01T00:00")
    closed = await auth_client.get("/bills")

    assert preview["total"] == 3
    assert closed.status_code == 200
    assert closed.json() == []


async def test_preview_includes_currency(auth_client: AsyncClient):
    preview = await get_bill(auth_client, "2026-10-01T00:00", "2026-11-01T00:00")

    assert preview["currency"] == currency


async def test_closed_bills_include_currency(
    auth_client: AsyncClient, monkeypatch: pytest.MonkeyPatch
):
    freeze_bill_time(monkeypatch, datetime(2026, 11, 1, 3, 0, tzinfo=timezone.utc))

    closed = await close_bill(auth_client, 2026, 10)
    listed = await auth_client.get("/bills")

    assert closed.status_code == 201
    assert closed.json()["currency"] == currency
    assert listed.status_code == 200
    assert listed.json()[0]["currency"] == currency


async def test_cannot_close_month_before_three_hour_grace_period(
    auth_client: AsyncClient, monkeypatch: pytest.MonkeyPatch
):
    freeze_bill_time(monkeypatch, datetime(2026, 10, 1, 2, 59, tzinfo=timezone.utc))

    response = await close_bill(auth_client, 2026, 9)

    assert response.status_code == 409
    assert response.json()["detail"] == "The month has not ended yet."
    assert (await auth_client.get("/bills")).json() == []


async def test_close_month_at_grace_period_boundary_persists_bill(
    auth_client: AsyncClient, monkeypatch: pytest.MonkeyPatch
):
    freeze_bill_time(monkeypatch, datetime(2026, 10, 1, 3, 0, tzinfo=timezone.utc))
    await ride(auth_client, "2026-09-30T23:00", "2026-09-30T23:30")
    await ride(auth_client, "2026-10-01T00:00", "2026-10-01T00:30")

    response = await close_bill(auth_client, 2026, 9)

    assert response.status_code == 201
    closed = response.json()
    assert closed["year"] == 2026
    assert closed["month"] == 9
    assert closed["total"] == 3
    assert closed["tickets"] == [
        {
            "type": "single_ticket",
            "valid_from": "2026-09-30T23:00:00",
            "price": 3,
        }
    ]
    assert closed["closed_at"].startswith("2026-10-01T03:00:00")

    listed = await auth_client.get("/bills")
    assert listed.status_code == 200
    assert listed.json() == [closed]


async def test_closing_month_without_trips_creates_zero_bill(
    auth_client: AsyncClient, monkeypatch: pytest.MonkeyPatch
):
    freeze_bill_time(monkeypatch, datetime(2026, 11, 1, 3, 0, tzinfo=timezone.utc))

    response = await close_bill(auth_client, 2026, 10)

    assert response.status_code == 201
    assert response.json()["tickets"] == []
    assert response.json()["total"] == 0


async def test_closing_same_month_twice_returns_conflict(
    auth_client: AsyncClient, monkeypatch: pytest.MonkeyPatch
):
    freeze_bill_time(monkeypatch, datetime(2026, 11, 1, 3, 0, tzinfo=timezone.utc))

    first = await close_bill(auth_client, 2026, 10)
    second = await close_bill(auth_client, 2026, 10)

    assert first.status_code == 201
    assert second.status_code == 409
    assert second.json()["detail"] == "Bill is already closed."
    assert len((await auth_client.get("/bills")).json()) == 1


async def test_closed_bills_are_user_scoped_and_sorted_by_month(
    auth_client: AsyncClient,
    make_auth_client: MakeAuthClient,
    monkeypatch: pytest.MonkeyPatch,
):
    freeze_bill_time(monkeypatch, datetime(2026, 11, 1, 3, 0, tzinfo=timezone.utc))
    other_client = await make_auth_client("other-bill-user@example.com")

    september = await close_bill(auth_client, 2026, 9)
    october = await close_bill(auth_client, 2026, 10)
    other_october = await close_bill(other_client, 2026, 10)

    assert (
        september.status_code == october.status_code == other_october.status_code == 201
    )
    response = await auth_client.get("/bills")

    assert response.status_code == 200
    assert [(bill["year"], bill["month"]) for bill in response.json()] == [
        (2026, 10),
        (2026, 9),
    ]


@pytest.mark.parametrize("year,month", [(2025, 9), (2026, 0), (2026, 13), (2201, 1)])
async def test_close_bill_rejects_invalid_period(
    auth_client: AsyncClient, year: int, month: int
):
    response = await close_bill(auth_client, year, month)

    assert response.status_code == 422
