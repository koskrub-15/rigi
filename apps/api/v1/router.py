from fastapi import APIRouter
from apps.api.v1.endpoints.scans import scan_router
from apps.api.v1.endpoints.trips import trip_router

api_router = APIRouter()
user_router = APIRouter(prefix="/user/{user_id}", tags=["users"])
api_router.include_router(user_router)
user_router.include_router(scan_router)
user_router.include_router(trip_router)
