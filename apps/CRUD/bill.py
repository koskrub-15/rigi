from datetime import datetime
from apps.schemas.bill import BillResponse
from sqlalchemy.ext.asyncio import AsyncSession
from apps.models.bill import BillModel
from collections.abc import Sequence
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError


async def create_bill_model(
    bill: BillResponse,
    db: AsyncSession,
    user_id: int,
    year: int,
    month: int,
    closed_at: datetime,
) -> BillModel | None:
    create_data = bill.model_dump(mode="json")
    model = BillModel
    db_obj = model(
        user_id=user_id, year=year, month=month, closed_at=closed_at, **create_data
    )
    db.add(db_obj)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        return None
    await db.refresh(db_obj)

    return db_obj


async def get_bills(db: AsyncSession, user_id: int) -> Sequence[BillModel]:
    result = await db.scalars(
        select(BillModel)
        .where(BillModel.user_id == user_id)
        .order_by(BillModel.year.desc(), BillModel.month.desc())
    )
    return result.all()


async def get_bill(db: AsyncSession, user_id: int, bill_id: int) -> BillModel | None:
    result = await db.scalars(
        select(BillModel)
        .where(BillModel.user_id == user_id)
        .where(BillModel.id == bill_id)
    )
    return result.one_or_none()
