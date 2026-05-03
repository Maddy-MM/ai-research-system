import pytest
from unittest.mock import patch, AsyncMock


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_research_run_success(client, auth_headers, mock_pipeline):
    """
    Valid token + valid topic should return 200 with report and feedback.
    mock_pipeline fixture ensures no real LLM or Tavily calls are made.
    """
    response = await client.post(
        "/research/run",
        json={"topic": "artificial intelligence"},
        headers=auth_headers,
    )
    assert response.status_code == 200

    body = response.json()

    # Check all expected fields are present
    assert "request_id" in body
    assert "topic" in body
    assert "report" in body
    assert "feedback" in body

    # Check values match what our mock returns
    assert body["topic"] == "artificial intelligence"
    assert body["report"] == "Mocked research report"
    assert "Score: 8/10" in body["feedback"]

    # request_id should be a UUID string
    assert len(body["request_id"]) == 36  # standard UUID format with hyphens

    # Confirm the mock was actually called once with our topic
    mock_pipeline.assert_called_once()
    call_kwargs = mock_pipeline.call_args.kwargs
    assert call_kwargs["topic"] == "artificial intelligence"


# ---------------------------------------------------------------------------
# Auth failures
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_research_run_no_token(client):
    """Request without Authorization header should return 401."""
    response = await client.post(
        "/research/run",
        json={"topic": "artificial intelligence"},
        # no headers
    )
    assert response.status_code == 401


@pytest.mark.anyio
async def test_research_run_invalid_token(client):
    """A made-up token that wasn't signed by our secret should return 401."""
    response = await client.post(
        "/research/run",
        json={"topic": "artificial intelligence"},
        headers={"Authorization": "Bearer this.is.not.a.real.token"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or expired token"


@pytest.mark.anyio
async def test_research_run_malformed_header(client):
    """
    Authorization header present but wrong format (no 'Bearer' prefix)
    should return 401.
    """
    response = await client.post(
        "/research/run",
        json={"topic": "artificial intelligence"},
        headers={"Authorization": "Token somefaketoken"},
    )
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# Pipeline failure
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_research_run_pipeline_error(client, auth_headers):
    """
    If the pipeline raises an unexpected exception, the route should
    catch it and return 500 — not crash the server or leak a traceback.

    Note: we don't use the mock_pipeline fixture here because we want
    to control the exception ourselves with a fresh patch.
    """
    with patch(
        "api.routes_research.run_research_pipeline",
        side_effect=Exception("Groq API is down"),
    ):
        response = await client.post(
            "/research/run",
            json={"topic": "artificial intelligence"},
            headers=auth_headers,
        )

    assert response.status_code == 500
    assert "Pipeline failed" in response.json()["detail"]


# ---------------------------------------------------------------------------
# Input validation
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_research_run_missing_topic(client, auth_headers):
    """
    Request body missing the 'topic' field should return 422
    before it even reaches the pipeline — Pydantic catches it first.
    """
    response = await client.post(
        "/research/run",
        json={},  # empty body
        headers=auth_headers,
    )
    assert response.status_code == 422