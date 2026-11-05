import jwt
import pytest
from httpx import AsyncClient

from apps.core.config import settings
from apps.core.security import create_access_token, create_zone_token


async def test_valid_zone_code_creates_scan_with_its_zone(auth_client: AsyncClient):
    response = await auth_client.post(
        "/scans",
        json={
            "scan_type": "check_in",
            "timestamp": "2026-10-14T08:00",
            "code": create_zone_token("B"),
        },
    )

    assert response.status_code == 201
    assert response.json()["zone"] == "B"


@pytest.mark.parametrize(
    "code",
    [
        pytest.param(
            jwt.encode(
                {"type": "zone", "zone": "A"},
                settings.SECRET_KEY + "-foreign",
                algorithm=settings.ALGORITHM,
            ),
            id="foreign-signing-key",
        ),
        pytest.param(create_access_token("1"), id="access-token"),
        pytest.param(
            jwt.encode(
                {"type": "access", "zone": "A"},
                settings.SECRET_KEY,
                algorithm=settings.ALGORITHM,
            ),
            id="wrong-type-with-zone",
        ),
        pytest.param(create_zone_token("Z"), id="unknown-zone"),
        pytest.param("junk", id="junk"),
    ],
)
async def test_invalid_zone_code_is_rejected(auth_client: AsyncClient, code: str):
    response = await auth_client.post(
        "/scans",
        json={
            "scan_type": "check_in",
            "timestamp": "2026-10-14T08:00",
            "code": code,
        },
    )

    assert response.status_code == 422


async def test_zone_code_cannot_authenticate_as_bearer(client: AsyncClient):
    response = await client.post(
        "/scans",
        headers={"Authorization": f"Bearer {create_zone_token('A')}"},
        json={
            "scan_type": "check_in",
            "timestamp": "2026-10-14T08:00",
            "code": create_zone_token("A"),
        },
    )

    assert response.status_code == 401
