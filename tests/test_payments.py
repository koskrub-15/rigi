from datetime import datetime, timezone
from types import SimpleNamespace

import stripe
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.v1.endpoints import bills as bills_endpoint
from apps.core.tariffs import currency
from apps.models.bill import BillModel
from apps.models.user import User
from apps.services import payments
from tests.conftest import MakeAuthClient


async def add_bill(db_session: AsyncSession, email: str, total: int) -> BillModel:
    user = await db_session.scalar(select(User).where(User.email == email))
    assert user is not None
    bill = BillModel(
        user_id=user.id,
        year=2026,
        month=10,
        tickets=[],
        total=total,
        closed_at=datetime(2026, 11, 1, 3, tzinfo=timezone.utc),
    )
    db_session.add(bill)
    await db_session.commit()
    await db_session.refresh(bill)
    return bill


async def test_pay_bill_returns_checkout_url_and_sends_expected_payment_data(
    auth_client: AsyncClient,
    db_session: AsyncSession,
    monkeypatch,
):
    bill = await add_bill(db_session, "user@example.com", total=12)
    captured_params = {}

    async def create_checkout_session(*, params):
        captured_params.update(params)
        return SimpleNamespace(url="https://checkout.example/session")

    monkeypatch.setattr(
        payments.client.v1.checkout.sessions,
        "create_async",
        create_checkout_session,
    )

    response = await auth_client.post(f"/bills/{bill.id}/payment")

    assert response.status_code == 200
    assert response.json() == {"url": "https://checkout.example/session"}
    line_item = captured_params["line_items"][0]
    assert line_item["price_data"]["unit_amount"] == bill.total * 100
    assert line_item["price_data"]["currency"] == currency
    assert captured_params["metadata"] == {"bill_id": str(bill.id)}


async def test_pay_bill_rejects_bill_owned_by_another_user(
    auth_client: AsyncClient,
    db_session: AsyncSession,
    make_auth_client: MakeAuthClient,
):
    bill = await add_bill(db_session, "user@example.com", total=12)
    other_client = await make_auth_client("other-payment-user@example.com")

    response = await other_client.post(f"/bills/{bill.id}/payment")

    assert response.status_code == 404


async def test_pay_bill_rejects_zero_total(
    auth_client: AsyncClient, db_session: AsyncSession
):
    bill = await add_bill(db_session, "user@example.com", total=0)

    response = await auth_client.post(f"/bills/{bill.id}/payment")

    assert response.status_code == 409


async def test_pay_bill_maps_stripe_error_to_bad_gateway(
    auth_client: AsyncClient,
    db_session: AsyncSession,
    monkeypatch,
):
    bill = await add_bill(db_session, "user@example.com", total=12)

    async def create_payment_url(bill: BillModel) -> str:
        raise stripe.StripeError("Stripe request failed")

    monkeypatch.setattr(bills_endpoint, "create_payment_url", create_payment_url)

    response = await auth_client.post(f"/bills/{bill.id}/payment")

    assert response.status_code == 502
