import pytest
from unittest.mock import patch, AsyncMock


@pytest.mark.anyio
async def test_research_run_success(client, auth_headers, mock_pipeline):
    response = await client.post(
        "/research/run",
        json={"topic": "artificial intelligence"},
        headers=auth_headers,
    )
    assert response.status_code == 200

    body = response.json()
    assert "request_id" in body
    assert "topic" in body
    assert "report" in body
    assert "feedback" in body
    assert "verification" in body
    assert "critic_score" in body
    assert "iteration_count" in body
    assert "tokens_used" in body
    assert "sub_questions" in body

    assert body["topic"] == "artificial intelligence"
    assert body["report"] == "Mocked research report"
    assert "Score: 8/10" in body["feedback"]
    assert "3/3 claims fully supported" in body["verification"]
    assert body["clarifying_question"] is None
    assert body["critic_score"] == 0.8
    assert body["iteration_count"] == 1
    assert body["tokens_used"] == 1500
    assert body["sub_questions"] == ["What is modern AI?"]

    assert len(body["request_id"]) == 36

    mock_pipeline.assert_called_once()
    call_kwargs = mock_pipeline.call_args.kwargs
    assert call_kwargs["topic"] == "artificial intelligence"


@pytest.mark.anyio
async def test_research_run_no_token(client):
    response = await client.post(
        "/research/run",
        json={"topic": "artificial intelligence"},
    )
    assert response.status_code == 401


@pytest.mark.anyio
async def test_research_run_invalid_token(client):
    response = await client.post(
        "/research/run",
        json={"topic": "artificial intelligence"},
        headers={"Authorization": "Bearer this.is.not.a.real.token"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or expired token"


@pytest.mark.anyio
async def test_research_run_malformed_header(client):
    response = await client.post(
        "/research/run",
        json={"topic": "artificial intelligence"},
        headers={"Authorization": "Token somefaketoken"},
    )
    assert response.status_code == 401


@pytest.mark.anyio
async def test_research_run_pipeline_error(client, auth_headers):
    with patch(
        "api.routes_research.run_research_pipeline",
        side_effect=Exception("LLM API is down"),
    ):
        response = await client.post(
            "/research/run",
            json={"topic": "artificial intelligence"},
            headers=auth_headers,
        )

    assert response.status_code == 500
    assert "Pipeline failed" in response.json()["detail"]


@pytest.mark.anyio
async def test_research_run_clarifying_question(client, auth_headers):
    fake_clarification = {
        "topic": "apple",
        "clarifying_question": "Did you mean Apple Inc. or the fruit?",
        "report": None,
        "feedback": None,
        "verification_summary": None,
    }
    with patch(
        "api.routes_research.run_research_pipeline",
        return_value=fake_clarification,
    ):
        response = await client.post(
            "/research/run",
            json={"topic": "apple"},
            headers=auth_headers,
        )

    assert response.status_code == 200
    body = response.json()
    assert body["report"] is None
    assert body["feedback"] is None
    assert body["verification"] is None
    assert body["clarifying_question"] == "Did you mean Apple Inc. or the fruit?"


@pytest.mark.anyio
async def test_research_run_missing_topic(client, auth_headers):
    response = await client.post(
        "/research/run",
        json={},
        headers=auth_headers,
    )
    assert response.status_code == 422


@pytest.mark.anyio
async def test_root_serves_jinja_index(client):
    response = await client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")
    assert "ResearchMind" in response.text