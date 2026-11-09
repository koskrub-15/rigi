import hashlib
import hmac
import json
import time
from datetime import datetime, timezone

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from apps.core.config import settings
from tests.test_payments import add_bill


def signed_event(
    event_type: str,
    secret: str,
    bill_id: int | str | None = "1",
    payment_status: str = "paid",
) -> tuple[str, str]:
    session: dict[str, object] = {
        "id": "cs_test",
        "object": "checkout.session",
        "payment_status": payment_status,
    }
    if bill_id is not None:
        session["metadata"] = {"bill_id": str(bill_id)}
    payload = json.dumps(
        {
            "id": "evt_test",
            "object": "event",
            "type": event_type,
            "data": {"object": session},
        },
        separators=(",", ":"),
    )
    timestamp = int(time.time())
    signed_content = f"{timestamp}.{payload}".encode()
    signature = hmac.new(secret.encode(), signed_content, hashlib.sha256).hexdigest()
    return payload, f"t={timestamp},v1={signature}"


async def post_signed_event(client: AsyncClient, payload: str, signature: str):
    return await client.post(
        "/stripe/webhook",
        content=payload,
        headers={"stripe-signature": signature},
    )


async def test_paid_checkout_event_marks_bill_paid(
    client: AsyncClient,
    db_session: AsyncSession,
    auth_client: AsyncClient,
    monkeypatch,
):
    secret = "webhook-test-secret"
    monkeypatch.setattr(settings, "STRIPE_WEBHOOK_SECRET", secret)
    bill = await add_bill(db_session, "user@example.com", total=12)
    payload, signature = signed_event(
        "checkout.session.completed", secret, bill_id=bill.id
    )

    response = await post_signed_event(client, payload, signature)

    assert response.status_code == 200
    assert response.json() == {"received": True}
    await db_session.refresh(bill)
    assert bill.paid_at is not None


async def test_paid_checkout_event_does_not_change_existing_paid_at(
    client: AsyncClient,
    db_session: AsyncSession,
    auth_client: AsyncClient,
    monkeypatch,
):
    secret = "webhook-test-secret"
    monkeypatch.setattr(settings, "STRIPE_WEBHOOK_SECRET", secret)
    bill = await add_bill(db_session, "user@example.com", total=12)
    bill.paid_at = datetime(2026, 11, 2, 12, tzinfo=timezone.utc)
    await db_session.commit()
    await db_session.refresh(bill)
    original_paid_at = bill.paid_at
    payload, signature = signed_event(
        "checkout.session.completed", secret, bill_id=bill.id
    )

    response = await post_signed_event(client, payload, signature)

    assert response.status_code == 200
    await db_session.refresh(bill)
    assert bill.paid_at == original_paid_at


async def test_unpaid_checkout_event_does_not_mark_bill_paid(
    client: AsyncClient,
    db_session: AsyncSession,
    auth_client: AsyncClient,
    monkeypatch,
):
    secret = "webhook-test-secret"
    monkeypatch.setattr(settings, "STRIPE_WEBHOOK_SECRET", secret)
    bill = await add_bill(db_session, "user@example.com", total=12)
    payload, signature = signed_event(
        "checkout.session.completed",
        secret,
        bill_id=bill.id,
        payment_status="unpaid",
    )

    response = await post_signed_event(client, payload, signature)

    assert response.status_code == 200
    assert response.json() == {"received": True}
    await db_session.refresh(bill)
    assert bill.paid_at is None


async def test_other_stripe_event_is_acknowledged_without_marking_bill_paid(
    client: AsyncClient,
    db_session: AsyncSession,
    auth_client: AsyncClient,
    monkeypatch,
):
    secret = "webhook-test-secret"
    monkeypatch.setattr(settings, "STRIPE_WEBHOOK_SECRET", secret)
    bill = await add_bill(db_session, "user@example.com", total=12)
    payload, signature = signed_event("customer.created", secret, bill_id=bill.id)

    response = await post_signed_event(client, payload, signature)

    assert response.status_code == 200
    assert response.json() == {"received": True}
    await db_session.refresh(bill)
    assert bill.paid_at is None


async def test_paid_event_for_unknown_bill_is_acknowledged(
    client: AsyncClient, monkeypatch
):
    secret = "webhook-test-secret"
    monkeypatch.setattr(settings, "STRIPE_WEBHOOK_SECRET", secret)
    payload, signature = signed_event(
        "checkout.session.completed", secret, bill_id="999999"
    )

    response = await post_signed_event(client, payload, signature)

    assert response.status_code == 200
    assert response.json() == {"received": True}


async def test_paid_event_without_bill_id_is_acknowledged_without_payment(
    client: AsyncClient,
    db_session: AsyncSession,
    auth_client: AsyncClient,
    monkeypatch,
):
    secret = "webhook-test-secret"
    monkeypatch.setattr(settings, "STRIPE_WEBHOOK_SECRET", secret)
    bill = await add_bill(db_session, "user@example.com", total=12)
    payload, signature = signed_event(
        "checkout.session.completed", secret, bill_id=None
    )

    response = await post_signed_event(client, payload, signature)

    assert response.status_code == 200
    assert response.json() == {"received": True}
    await db_session.refresh(bill)
    assert bill.paid_at is None


async def test_webhook_rejects_invalid_signature(client: AsyncClient, monkeypatch):
    secret = "webhook-test-secret"
    monkeypatch.setattr(settings, "STRIPE_WEBHOOK_SECRET", secret)
    payload, signature = signed_event("checkout.session.completed", secret)
    timestamp = signature.split(",", maxsplit=1)[0]

    response = await post_signed_event(client, payload, f"{timestamp},v1=invalid")

    assert response.status_code == 400
