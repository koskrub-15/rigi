from datetime import timedelta

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from apps.core.security import create_access_token, create_zone_token
from apps.CRUD.user import create_user
from apps.schemas.user import UserCreate

from tests.conftest import MakeAuthClient

USER = {
    "email": "anna@example.com",
    "first_name": "Anna",
    "last_name": "Berg",
    "password": "password123",
}


async def register_and_login(client: AsyncClient) -> dict:
    await client.post("/auth/register", json=USER)
    response = await client.post(
        "/auth/login",
        data={"username": USER["email"], "password": USER["password"]},
    )
    assert response.status_code == 200
    return response.json()


async def test_register_returns_user_without_password(client: AsyncClient):
    response = await client.post("/auth/register", json=USER)

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == USER["email"]
    assert "password" not in body
    assert "hashed_password" not in body


async def test_register_duplicate_email_is_rejected(client: AsyncClient):
    await client.post("/auth/register", json=USER)

    response = await client.post(
        "/auth/register", json={**USER, "email": USER["email"].upper()}
    )

    assert response.status_code == 409


async def test_create_user_returns_none_for_taken_email(db_session: AsyncSession):
    data = UserCreate(**USER)

    assert await create_user(db_session, data) is not None
    assert await create_user(db_session, data) is None


async def test_login_is_case_insensitive_for_email(client: AsyncClient):
    await client.post("/auth/register", json=USER)

    response = await client.post(
        "/auth/login",
        data={"username": USER["email"].upper(), "password": USER["password"]},
    )

    assert response.status_code == 200


async def test_login_wrong_password_returns_401(client: AsyncClient):
    await client.post("/auth/register", json=USER)

    response = await client.post(
        "/auth/login", data={"username": USER["email"], "password": "wrong-password"}
    )

    assert response.status_code == 401


async def test_protected_endpoint_requires_token(client: AsyncClient):
    response = await client.get("/trips")

    assert response.status_code == 401


async def test_expired_access_token_returns_401(client: AsyncClient):
    user = (await client.post("/auth/register", json=USER)).json()
    expired = create_access_token(user["id"], timedelta(seconds=-1))

    response = await client.get(
        "/trips", headers={"Authorization": f"Bearer {expired}"}
    )

    assert response.status_code == 401


async def test_refresh_token_cannot_be_used_as_access_token(client: AsyncClient):
    tokens = await register_and_login(client)

    response = await client.get(
        "/trips", headers={"Authorization": f"Bearer {tokens['refresh_token']}"}
    )

    assert response.status_code == 401


async def test_refresh_token_is_single_use(client: AsyncClient):
    tokens = await register_and_login(client)
    body = {"refresh_token": tokens["refresh_token"]}

    first = await client.post("/auth/refresh", json=body)
    reuse = await client.post("/auth/refresh", json=body)

    assert first.status_code == 200
    assert first.json()["refresh_token"] != tokens["refresh_token"]
    assert reuse.status_code == 401


async def test_logout_revokes_refresh_token(client: AsyncClient):
    tokens = await register_and_login(client)
    body = {"refresh_token": tokens["refresh_token"]}

    logout = await client.post("/auth/logout", json=body)
    second_logout = await client.post("/auth/logout", json=body)
    refresh = await client.post("/auth/refresh", json=body)

    assert logout.status_code == 200
    assert second_logout.status_code == 200
    assert refresh.status_code == 401


async def test_users_only_see_their_own_trips(
    auth_client: AsyncClient, make_auth_client: MakeAuthClient
):
    other_client = await make_auth_client("other@example.com")
    for scan_type, timestamp in [
        ("check_in", "2026-10-14T08:00"),
        ("check_out", "2026-10-14T08:30"),
    ]:
        response = await other_client.post(
            "/scans",
            json={
                "scan_type": scan_type,
                "timestamp": timestamp,
                "code": create_zone_token("A"),
            },
        )
        assert response.status_code == 201

    assert (await other_client.get("/trips")).json() != []
    assert (await auth_client.get("/trips")).json() == []
