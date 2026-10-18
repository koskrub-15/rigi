from apps.db.session import get_db
from fastapi import status, APIRouter, Depends
from apps.schemas.scan import ScanCreate, ScanResponse
from apps.CRUD.scan import create_scan
from sqlalchemy.ext.asyncio import AsyncSession


scan_router = APIRouter(prefix="/scans", tags=["scans"])


@scan_router.post("", response_model=ScanResponse, status_code=status.HTTP_201_CREATED)
async def create_scan_endpoint(
    data: ScanCreate, user_id: int, db: AsyncSession = Depends(get_db)
):
    """Create a scan"""
    return await create_scan(scan=data, db=db, user_id=user_id)
