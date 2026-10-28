from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import AsyncExitStack

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from apps.db.session import get_db
from apps.main import app
from apps.models import Base

engine = create_async_engine(
    "sqlite+aiosqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = async_sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)


@pytest_asyncio.fixture(name="db_session")
async def db_session_fixture():
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)

    async with TestingSessionLocal() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture(name="client")
async def client_fixture(db_session: AsyncSession):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client

    app.dependency_overrides.clear()


MakeAuthClient = Callable[[str], Awaitable[AsyncClient]]


@pytest_asyncio.fixture(name="make_auth_client")
async def make_auth_client_fixture(
    client: AsyncClient,
) -> AsyncIterator[MakeAuthClient]:
    """Factory: register a user by email and return a client logged in as them."""
    async with AsyncExitStack() as stack:

        async def make(email: str) -> AsyncClient:
            password = "password123"
            await client.post(
                "/auth/register",
                json={
                    "email": email,
                    "first_name": "Test",
                    "last_name": "User",
                    "password": password,
                },
            )
            login = await client.post(
                "/auth/login", data={"username": email, "password": password}
            )
            token = login.json()["access_token"]
            return await stack.enter_async_context(
                AsyncClient(
                    transport=ASGITransport(app=app),
                    base_url="http://test",
                    headers={"Authorization": f"Bearer {token}"},
                )
            )

        yield make


@pytest_asyncio.fixture(name="auth_client")
async def auth_client_fixture(make_auth_client: MakeAuthClient) -> AsyncClient:
    return await make_auth_client("user@example.com")
