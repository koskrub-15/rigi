from fastapi import FastAPI

from apps.api.v1.router import api_router
from fastapi.middleware.cors import CORSMiddleware
from apps.core.config import settings


app = FastAPI(title="rigi")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router)
