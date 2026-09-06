import pytest


from src.config import get_settings


@pytest.mark.anyio
async def test_login_success(client):
    settings = get_settings()
    response = await client.post(
        "/auth/token",
        data={"username": settings.DEMO_USERNAME, "password": settings.DEMO_PASSWORD},
    )
    assert response.status_code == 200

    body = response.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"
    assert isinstance(body["access_token"], str)
    assert len(body["access_token"]) > 0


@pytest.mark.anyio
async def test_login_wrong_password(client):
    settings = get_settings()
    response = await client.post(
        "/auth/token",
        data={"username": settings.DEMO_USERNAME, "password": "wrongpassword_never_matches"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"


@pytest.mark.anyio
async def test_login_wrong_username(client):
    settings = get_settings()
    response = await client.post(
        "/auth/token",
        data={"username": "hacker_unknown_user_xyz", "password": settings.DEMO_PASSWORD},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"


@pytest.mark.anyio
async def test_login_missing_fields(client):
    response = await client.post("/auth/token", data={})
    assert response.status_code == 422