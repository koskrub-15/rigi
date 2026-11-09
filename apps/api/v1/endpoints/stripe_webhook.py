from datetime import datetime, timezone
from fastapi import APIRouter, status, Depends, HTTPException, Request
from apps.db.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from apps.core.config import settings
from apps.services.payments import client
from apps.CRUD.bill import pay
import stripe


stripe_router = APIRouter(prefix="/stripe", tags=["stripe"])


@stripe_router.post("/webhook")
async def stripe_webhook(
    request: Request, db: AsyncSession = Depends(get_db)
) -> dict[str, bool]:
    payload = await request.body()
    sig = request.headers.get("stripe-signature")
    try:
        event = client.construct_event(payload, sig, settings.STRIPE_WEBHOOK_SECRET)
    except stripe.SignatureVerificationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST) from e

    if event.type == "checkout.session.completed":
        session = event.data.object
        pay_status = session.payment_status
        metadata = session.to_dict().get("metadata") or {}
        bill_id = metadata.get("bill_id")
        if bill_id is None:
            return {"received": True}
        if pay_status == "paid":
            await pay(db=db, bill_id=int(bill_id), now=datetime.now(timezone.utc))

    return {"received": True}
