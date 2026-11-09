from datetime import datetime, timezone
from collections.abc import Sequence
from apps.CRUD.bill import create_bill_model, get_bills, get_bill
from apps.core.tariffs import MAX_TRIP_DURATION
from apps.db.session import get_db
from apps.models.bill import BillModel
from apps.schemas.bill import BillResponse, ClosedBillResponse, PaymentResponse
from apps.services.trips import get_trips
from apps.services.optimizer import optimizer, total_price
from fastapi import APIRouter, Depends, status, Path, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession
from apps.api.deps import get_current_user
from apps.models.user import User
from apps.services.month import month_bounds_utc
from apps.services.payments import create_payment_url
import stripe


bill_router = APIRouter(prefix="/bills", tags=["bill"])


@bill_router.get("/preview", response_model=BillResponse)
async def create_bill(
    date_from: datetime,
    date_to: datetime,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BillResponse:
    """Create a month bill"""
    trips = await get_trips(
        user_id=current_user.id,
        date_from=date_from,
        date_to=date_to,
        now=datetime.now(timezone.utc),
        db=db,
    )
    tickets = optimizer(trips=trips)
    return BillResponse(tickets=tickets, total=total_price(tickets))


@bill_router.post("/{bill_id}/payment", response_model=PaymentResponse)
async def pay_bill(
    bill_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PaymentResponse:
    bill = await get_bill(bill_id=bill_id, db=db, user_id=current_user.id)
    if bill is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Bill doesn't exist"
        )
    if bill.paid_at is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Bill is already paid"
        )
    if bill.total != 0:
        try:
            return PaymentResponse(url=await create_payment_url(bill=bill))
        except stripe.StripeError as e:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY) from e

    else:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Bill is empty"
        )


@bill_router.post(
    "/{year}/{month}",
    response_model=ClosedBillResponse,
    status_code=status.HTTP_201_CREATED,
)
async def close_bill(
    year: int = Path(ge=2026, le=2200),
    month: int = Path(ge=1, le=12),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BillModel:
    start, end = month_bounds_utc(year, month)
    now = datetime.now(timezone.utc)
    if now < end + MAX_TRIP_DURATION:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="The month has not ended yet."
        )
    trips = await get_trips(
        user_id=current_user.id,
        date_from=start,
        date_to=end,
        now=now,
        db=db,
    )

    tickets = optimizer(trips=trips)
    response = BillResponse(tickets=tickets, total=total_price(tickets))
    create_in_bd: BillModel | None = await create_bill_model(
        bill=response,
        db=db,
        user_id=current_user.id,
        year=year,
        month=month,
        closed_at=now,
    )
    if create_in_bd is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Bill is already closed."
        )
    return create_in_bd


@bill_router.get("", response_model=list[ClosedBillResponse])
async def get_all_closed_bills(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Sequence[BillModel]:
    """Get all closed bills"""
    return await get_bills(db=db, user_id=current_user.id)
