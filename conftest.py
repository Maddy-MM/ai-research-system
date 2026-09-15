import sys
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "backend", ".env"))
# Always isolate tests to a local SQLite database so tests never modify production
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch

from main import app
from src.auth import create_access_token, get_user, create_user, hash_password
from src.database import init_db, SessionLocal
from src.config import get_settings


@pytest.fixture(autouse=True)
def setup_test_db():
    init_db()
    settings = get_settings()
    configured_user = os.environ.get("DEFAULT_USER") or getattr(settings, "effective_username", "admin")
    password = os.environ.get("DEFAULT_PASS") or getattr(settings, "effective_password", "secret")
    db = SessionLocal()
    try:
        for uname in {configured_user, "admin"}:
            user = get_user(db, uname)
            if not user:
                create_user(db, uname, password)
            else:
                user.hashed_password = hash_password(password)
                db.commit()
    finally:
        db.close()


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac


@pytest.fixture
def valid_token():
    settings = get_settings()
    return create_access_token(username=settings.effective_username)


@pytest.fixture
def auth_headers(valid_token):
    return {"Authorization": f"Bearer {valid_token}"}


@pytest.fixture
def mock_pipeline():
    fake_state = {
        "topic": "artificial intelligence",
        "sub_questions": ["What is modern AI?"],
        "research_results": [{"sub_question": "What is modern AI?", "content": "Mocked research"}],
        "report": "Mocked research report",
        "feedback": "Score: 8/10\n\nStrengths:\n- Good\n\nAreas to Improve:\n- More sources\n\nOne line verdict: Solid report.",
        "verification_summary": "3/3 claims fully supported, 0 partial, 0 unsupported.\nNo issues found.",
        "critic_score": 0.8,
        "iteration_count": 1,
        "tokens_used": 1500,
    }

    with patch(
        "api.routes_research.run_research_pipeline",
        return_value=fake_state,
    ) as mock:
        yield mock