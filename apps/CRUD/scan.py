from apps.models.scan import ScanModel, ScanType
from apps.schemas.scan import ScanCreate, ScanResponse
from sqlalchemy.ext.asyncio import AsyncSession
from collections.abc import Sequence
from sqlalchemy import select


async def create_scan(scan: ScanCreate, db: AsyncSession, user_id: int) -> ScanModel:
    create_data = scan.model_dump()
    model = ScanModel
    db_obj = model(user_id=user_id, **create_data)
    db.add(db_obj)

    await db.commit()
    await db.refresh(db_obj)

    return db_obj


async def get_scans(db: AsyncSession, user_id: int) -> Sequence[ScanModel]:
    result = await db.scalars(
        select(ScanModel)
        .where(user_id == ScanModel.user_id)
        .order_by(ScanModel.timestamp)
    )
    return result.all()
