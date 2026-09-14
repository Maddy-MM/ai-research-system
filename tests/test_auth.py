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


@pytest.mark.anyio
async def test_json_login_success(client):
    settings = get_settings()
    username = settings.effective_username
    password = settings.effective_password
    response = await client.post(
        "/login",
        json={"username": username, "password": password},
    )
    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"
    assert len(body["access_token"]) > 0


@pytest.mark.anyio
async def test_json_login_wrong_password(client):
    settings = get_settings()
    username = settings.effective_username
    response = await client.post(
        "/login",
        json={"username": username, "password": "wrongpassword"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"


@pytest.mark.anyio
async def test_auth_login_alias(client):
    settings = get_settings()
    username = settings.effective_username
    password = settings.effective_password
    response = await client.post(
        "/auth/login",
        json={"username": username, "password": password},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_bcrypt_hashing():
    from src.auth import hash_password, verify_password

    plain = "my-secret-password-123"
    hashed = hash_password(plain)
    assert hashed != plain
    assert hashed.startswith("$2b$") or hashed.startswith("$2a$")
    assert verify_password(plain, hashed) is True
    assert verify_password("wrong-guess", hashed) is False