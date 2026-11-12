import stripe
from apps.core.config import settings
from apps.core.tariffs import currency
from apps.models.bill import BillModel

client = stripe.StripeClient(
    settings.STRIPE_SECRET_KEY, http_client=stripe.HTTPXClient()
)


async def create_payment_url(bill: BillModel) -> str:
    session = await client.v1.checkout.sessions.create_async(
        params={
            "mode": "payment",
            "line_items": [
                {
                    "quantity": 1,
                    "price_data": {
                        "currency": currency,
                        "unit_amount": bill.total * 100,
                        "product_data": {"name": f"Rigi {bill.year}-{bill.month:02d}"},
                    },
                }
            ],
            "success_url": f"{settings.WEB_URL}/tickets?payment=success",
            "cancel_url": f"{settings.WEB_URL}/tickets?payment=cancel",
            "metadata": {"bill_id": str(bill.id)},
        }
    )
    return session.url
