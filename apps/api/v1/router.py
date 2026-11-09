from fastapi import APIRouter
from apps.api.v1.endpoints.scans import scan_router
from apps.api.v1.endpoints.trips import trip_router
from apps.api.v1.endpoints.bills import bill_router
from apps.api.v1.endpoints.stats import stats_router
from apps.api.v1.endpoints.auth import router as auth_router
from apps.api.v1.endpoints.stripe_webhook import stripe_router


api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(scan_router)
api_router.include_router(trip_router)
api_router.include_router(bill_router)
api_router.include_router(stats_router)
api_router.include_router(stripe_router)
