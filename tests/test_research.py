import pytest
from unittest.mock import patch


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
    assert "execution_time_seconds" in body

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


@pytest.mark.anyio
async def test_research_history_and_clear(client, auth_headers, mock_pipeline):
    # Run a research query
    post_res = await client.post(
        "/research/run",
        json={"topic": "Quantum Computing"},
        headers=auth_headers,
    )
    assert post_res.status_code == 200

    # Fetch history
    history_res = await client.get("/research/history", headers=auth_headers)
    assert history_res.status_code == 200
    history = history_res.json()
    assert len(history) >= 1
    assert any(h["topic"] == "Quantum Computing" for h in history)

    # Clear history
    clear_res = await client.delete("/research/history", headers=auth_headers)
    assert clear_res.status_code == 200
    assert clear_res.json()["status"] == "ok"

    # Verify history is empty
    history_res_after = await client.get("/research/history", headers=auth_headers)
    assert history_res_after.status_code == 200
    assert len(history_res_after.json()) == 0


@pytest.mark.anyio
async def test_delete_individual_history_item(client, auth_headers, mock_pipeline):
    # Run two research queries
    res1 = await client.post("/research/run", json={"topic": "Topic One"}, headers=auth_headers)
    res2 = await client.post("/research/run", json={"topic": "Topic Two"}, headers=auth_headers)
    assert res1.status_code == 200
    assert res2.status_code == 200

    req_id1 = res1.json()["request_id"]

    # Delete only the first item
    del_res = await client.delete(f"/research/history/{req_id1}", headers=auth_headers)
    assert del_res.status_code == 200
    assert del_res.json()["status"] == "ok"

    # Verify first is gone, second remains
    history_res = await client.get("/research/history", headers=auth_headers)
    assert history_res.status_code == 200
    topics = [h["topic"] for h in history_res.json()]
    assert "Topic One" not in topics
    assert "Topic Two" in topics

    # Trying to delete already deleted item returns 404
    del_res_404 = await client.delete(f"/research/history/{req_id1}", headers=auth_headers)
    assert del_res_404.status_code == 404