from contextlib import asynccontextmanager

from fastapi import FastAPI

from apps.api.v1.router import api_router
from apps.db.session import engine
from apps.models import Base
from fastapi.middleware.cors import CORSMiddleware
from apps.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # без alembic: при старте создаём таблицы, которых ещё нет
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title="rigi", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router)
