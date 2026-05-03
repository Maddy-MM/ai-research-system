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


# ---------------------------------------------------------------------------
# App client
# ---------------------------------------------------------------------------

@pytest.fixture
def anyio_backend():
    """Tells pytest-anyio to use asyncio as the async backend."""
    return "asyncio"


@pytest.fixture
async def client():
    """
    Async HTTP client that talks directly to the FastAPI app in-process.
    No real network calls — ASGITransport wires httpx straight into the app.
    This is FastAPI's recommended way to test async endpoints.
    """
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac


# ---------------------------------------------------------------------------
# Auth fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def valid_token():
    """
    Creates a real JWT signed with the same secret the app uses.
    We call create_access_token() directly — no HTTP round trip needed.
    This token is reused in every test that needs an authenticated request.
    """
    return create_access_token(username="admin")


@pytest.fixture
def auth_headers(valid_token):
    """
    Ready-made Authorization header dict.
    Usage in tests:
        response = await client.post("/research/run", headers=auth_headers, ...)
    """
    return {"Authorization": f"Bearer {valid_token}"}


# ---------------------------------------------------------------------------
# Pipeline mock
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_pipeline():
    """
    Patches run_research_pipeline so tests never call Tavily, Groq, or
    BeautifulSoup. The patch targets the function where it's *used*
    (routes_research), not where it's *defined* (pipeline.pipeline).
    This is the standard Python mocking rule.

    AsyncMock is needed because run_research_pipeline is an async function —
    a regular MagicMock would return a coroutine object instead of awaiting it.
    """
    fake_state = {
        "search_results": "Mocked search results",
        "scraped_content": "Mocked scraped content",
        "report": "Mocked research report",
        "feedback": "Score: 8/10\n\nStrengths:\n- Good\n\nAreas to Improve:\n- More sources\n\nOne line verdict: Solid report.",
    }

    with patch(
        "api.routes_research.run_research_pipeline",
        return_value=fake_state,
    ) as mock:
        yield mock