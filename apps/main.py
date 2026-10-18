from contextlib import asynccontextmanager

from fastapi import FastAPI

from apps.api.v1.router import api_router
from apps.db.session import engine
from apps.models.scan import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    # без alembic: при старте создаём таблицы, которых ещё нет
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title="rigi", lifespan=lifespan)
app.include_router(api_router)
