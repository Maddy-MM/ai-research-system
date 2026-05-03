import pytest


# ---------------------------------------------------------------------------
# All tests in this file are async because our FastAPI app and client are async.
# pytest.mark.anyio tells pytest-anyio to run them in an asyncio event loop.
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_login_success(client):
    """Valid credentials should return a 200 with an access token."""
    response = await client.post(
        "/auth/token",
        data={"username": "admin", "password": "secret"},  # form data, not JSON
    )
    assert response.status_code == 200

    body = response.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"
    # Token should be a non-empty string
    assert isinstance(body["access_token"], str)
    assert len(body["access_token"]) > 0


@pytest.mark.anyio
async def test_login_wrong_password(client):
    """Wrong password should return 401."""
    response = await client.post(
        "/auth/token",
        data={"username": "admin", "password": "wrongpassword"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"


@pytest.mark.anyio
async def test_login_wrong_username(client):
    """Wrong username should return 401."""
    response = await client.post(
        "/auth/token",
        data={"username": "hacker", "password": "secret"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"


@pytest.mark.anyio
async def test_login_missing_fields(client):
    """Missing form fields should return 422 Unprocessable Entity."""
    response = await client.post("/auth/token", data={})
    assert response.status_code == 422