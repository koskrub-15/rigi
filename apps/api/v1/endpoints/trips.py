from apps.db.session import get_db
from apps.models.scan import ScanModel
from apps.schemas.trip import TripResponse
from fastapi import FastAPI, HTTPException, Query, status, APIRouter, Depends
from apps.schemas.scan import ScanCreate, ScanResponse
from apps.CRUD.scan import get_scans
from sqlalchemy.ext.asyncio import AsyncSession
from apps.services.trips import build_trips

trip_router = APIRouter(prefix="/trips", tags=["trips"])


@trip_router.get("", response_model=list[TripResponse])
async def build_trips_endpoint(
    user_id: int,
    db: AsyncSession = Depends(get_db),
) -> list[TripResponse]:
    """Create trips"""
    return build_trips(scans=await get_scans(db=db, user_id=user_id))
