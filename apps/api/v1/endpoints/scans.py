from apps.db.session import get_db
from fastapi import status, APIRouter, Depends
from apps.schemas.scan import ScanCreate, ScanResponse
from apps.CRUD.scan import create_scan
from sqlalchemy.ext.asyncio import AsyncSession
from apps.models.user import User
from apps.api.deps import get_current_user


scan_router = APIRouter(prefix="/scans", tags=["scans"])


@scan_router.post("", response_model=ScanResponse, status_code=status.HTTP_201_CREATED)
async def create_scan_endpoint(
    data: ScanCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a scan"""
    return await create_scan(scan=data, db=db, user_id=current_user.id)
