from apps.db.session import get_db
from apps.schemas.trip import TripResponse
from fastapi import APIRouter, Depends
from apps.CRUD.scan import get_scans
from sqlalchemy.ext.asyncio import AsyncSession
from apps.services.trips import build_trips
from apps.models.user import User
from apps.api.deps import get_current_user

trip_router = APIRouter(prefix="/trips", tags=["trips"])


@trip_router.get("", response_model=list[TripResponse])
async def build_trips_endpoint(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[TripResponse]:
    """Create trips"""
    return build_trips(scans=await get_scans(db=db, user_id=current_user.id))
