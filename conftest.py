import sys
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "backend", ".env"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, AsyncMock

from backend.main import app
from backend.src.auth import create_access_token


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
    return create_access_token(username="admin")


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