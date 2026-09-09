# ResearchMind

A **multi-agent AI research pipeline** built on LangGraph: a planner breaks a topic into sub-questions, tool-using researcher agents investigate them in parallel via an MCP tool server, a writer drafts the report, a critic iteratively checks it for quality, and a tool-using verifier agent independently fact-checks it against fresh sources — all in a single pipeline run.

The pipeline combines structured LLM steps with autonomous tool-using agents, giving each stage a distinct role in producing the final report. Researchers independently investigate their assigned sub-questions and decide which tools and sources to use, while the verifier performs a separate pass over the finished report to validate its claims against fresh evidence. LangGraph coordinates these stages into a single workflow, allowing research, writing, critique, and verification to work together without relying on a fixed sequence of tool calls.

---

## Table of Contents

1. Overview
2. Features
3. Project Workflow
4. Pipeline Architecture
5. MCP Tool Server
6. Authentication
7. API Endpoints
8. Frontend
9. Project Structure
10. Installation & Setup
11. How to Run
12. Evaluation Harness
13. Testing
14. Deployment Architecture
15. Observability
16. Current Limitations & Tradeoffs
17. Future Improvements
18. Tech Stack

---

## Overview

ResearchMind implements an **end-to-end agentic research pipeline** as a LangGraph state machine:

- **FastAPI backend** orchestrates a multi-node graph with JWT auth, structured JSON logging, and Prometheus metrics
- **MCP tool server** exposes research tools (web search, scraping, arXiv, calculator) as a standalone FastMCP process, consumed by the graph as an MCP client
- **Modern Scholar-Tech Web Frontend:** Pure Vanilla HTML5 + CSS3 + ES6+ JavaScript, Jinja2 templating, and marked.js markdown rendering (with an optional legacy Streamlit prototype)
- **Unified Container Architecture:** Single Docker container hosting FastMCP, FastAPI, and the full web interface seamlessly

The system uses **LangGraph** to orchestrate planning, parallel research, writing, critique, and citation verification, backed by an OpenAI LLM.

---

## Live Demo

- **Backend & Web Application (Render):** [ResearchMind - Live App](https://researchmind.madhavmakwana.dev/)

> **Access:** Login required — access credentials are provided privately to authorized users (demo defaults: `admin` / `secret`).

---

## Features

- JWT-authenticated access — login required before using the app
- LangGraph-orchestrated pipeline: plan → research (parallel fan-out) → write → critique → verify
- Dynamic planning — sub-question count scales with topic complexity; can ask a clarifying question instead of researching an ambiguous topic
- Parallel research via LangGraph's `Send` API — sub-questions investigated concurrently, not sequentially
- MCP tool server exposing `web_search`, `scrape_url`, `arxiv_search`, and `calculator` — shared by both the researcher agent (per sub-question) and the verifier agent, each selecting tools independently
- Iterative critic loop — structured verdict (score + issue type) routes back to the planner (missing info) or the writer (unclear/unsupported), bounded by an iteration cap and a token budget
- Independent citation verification — a tool-using verifier agent re-checks the report's most load-bearing claims against fresh sources (not just the original research), then a structured chain gives a yes/no/partial verdict per claim
- Optional LangSmith tracing for full pipeline observability during development
- Prometheus metrics for pipeline observability
- Structured JSON logging across all backend components
- Production Scholar-Tech UI with Obsidian/Solar-Amber aesthetic, Screen 0 Login, collapsible enquiry history sidebar, open-air SVG circuit schematic, Screen 2 Dossier with bounded scrollable verification/critic panels, and markdown/print exports
- Full async test suite with mocked pipeline

---

## Project Workflow

1. User logs in with username and password
2. JWT token issued and stored for the session
3. User enters a research topic
4. **Planner** breaks the topic into sub-questions (or asks a clarifying question if too ambiguous)
5. **Researchers** investigate each sub-question in parallel, each selecting tools from the MCP server
6. **Writer** drafts a structured report from all research findings
7. **Critic** scores the report; if below threshold, routes back to planner or writer for another pass
8. **Verifier** independently re-checks the report's most load-bearing claims against fresh sources via its own tool calls, then gives a yes/no/partial verdict on every claim
9. Results — report, critic feedback, and verification summary — rendered on a dedicated screen

---

## Pipeline Architecture

Built as a LangGraph `StateGraph` with conditional routing:

```
                  ┌─→ END (clarifying_question)
START → planner ──┴─→ [Send fan-out] → researcher (parallel) → write → critique ─┬─→ planner (missing_info)
                                                                                 ├─→ write (unclear/unsupported)
                                                                                 └─→ verify → END
```

### Planner
- Structured output (`sub_questions`, `clarifying_question`) via `with_structured_output`
- Varies sub-question count with topic complexity instead of a fixed count
- On a critic re-route (`missing_info`), regenerates sub-questions informed by what the previous draft was missing

### Researcher (parallel)
- One LangGraph node instance per sub-question, dispatched concurrently via `Send`
- Each instance is an MCP *client* — connects to the tool server and picks whichever tool(s) fit the sub-question
- Results accumulate into shared graph state via a list-append reducer

### Writer
- Combines all parallel research results into one structured report (Introduction, Key Findings, Conclusion, Sources)

### Critic
- Structured verdict: `{score, issue_type, strengths, areas_to_improve, verdict}`
- `issue_type` drives routing: `missing_info` → back to planner, `unclear_writing`/`unsupported_claims` → back to writer, `none` → proceed to verification
- Bounded by `MAX_ITERATIONS` and a per-run token budget — either forces exit regardless of score

### Verifier
- Runs after the critic passes — first runs as its own MCP tool-using agent, independently re-checking the report's most load-bearing claims against fresh sources rather than only the original research
- Those independent findings are combined with the original research, then a structured chain gives a per-claim yes/no/partial verdict against the combined context
- Produces a human-readable summary of unsupported or partially-supported claims

---

## MCP Tool Server

A standalone process (`src/mcp_server/server.py`) exposing four tools over MCP:

- `web_search` — Tavily-backed web search
- `scrape_url` — BeautifulSoup-based page scraping
- `arxiv_search` — academic paper search via the arXiv API
- `calculator` — safe arithmetic evaluation (no `eval`/`exec`)

Two nodes connect as MCP clients (`langchain-mcp-adapters`), each an independent tool-calling agent: the **researcher** picks tool(s) per sub-question, and the **verifier** independently picks tool(s) to spot-check the report's claims — neither follows a fixed search→scrape sequence.

---

## Authentication

ResearchMind uses **JWT-based authentication**. A login is required before accessing any part of the application.

- Passwords are verified against a hardcoded admin user configured via environment variables
- On login, the backend issues a signed JWT token
- All protected endpoints verify the token via a FastAPI `HTTPBearer` dependency

**Public endpoints:** `/health`, `/auth/token`
**Protected endpoints:** `/research/run`, `/research/history`

---

## API Endpoints

### Health Check
`GET /health` — Returns `{"status": "ok"}`.

### Login
`POST /auth/token` — Accepts form data `username` and `password`. Returns a signed JWT `access_token` on success, HTTP 401 on invalid credentials.

### Run Pipeline
`POST /research/run` _(protected)_ — Accepts JSON `{"topic": "..."}`. Runs the full graph, persists the report to database, and returns:

```json
{
  "request_id": "uuid",
  "topic": "...",
  "report": "...",
  "feedback": "...",
  "verification": "...",
  "clarifying_question": null,
  "critic_score": 0.8,
  "iteration_count": 1,
  "tokens_used": 1500,
  "sub_questions": ["..."]
}
```

`report`/`feedback`/`verification` are `null` and `clarifying_question` is populated instead if the planner judged the topic too ambiguous to research directly.

### Research History
`GET /research/history` _(protected)_ — Returns recent research dossiers for the authenticated user from the database.

### Clear History
`DELETE /research/history` _(protected)_ — Clears all saved research history for the authenticated user.

### Delete Single Report
`DELETE /research/history/{request_id}` _(protected)_ — Deletes a specific research dossier by its UUID request ID.

---

## Frontend

ResearchMind features a production **Pure Vanilla Modern Web Interface** (HTML5 + CSS3 + ES6+ JavaScript) served directly via FastAPI and Jinja2:

- **No Heavy Frameworks:** Zero React, Vue, or Tailwind bloat — single centralized stylesheet with custom CSS variables and an Obsidian/Solar-Amber "Scholar-Tech" aesthetic.
- **Screen 0 (Login View):** Clean obsidian glass card with demo credential quick-fill, password reveal, and real-time JWT token state.
- **Left Sidebar:** Collapsible drawer with "New Research" trigger, elevated Recent Enquiries deck with local storage caching, live engine telemetry, GitHub repository link, and Sign Out action.
- **Screen 1 (Search & Pipeline Cockpit):** Split view with query input, inquiry focus pills, search depth toggles, and an interactive SVG circuit schematic diagram visualizing the 5 LangGraph stages.
- **Telemetry Modal:** Live animated modal with stage progress stepper, monospace timer, neural canvas, and active phase status updates.
- **Screen 2 (Results & Dossier View):** Top action bar (Export Markdown, Export PDF, Print, Share, New Research), metrics strip (word count, sources vetted, execution time, token metrics), rendered Markdown report via `marked.js`, and side-by-side bounded scrollable cards for **Independent Verification** (claim fact-checking) and **Critic Review** (quality scoring & reflection loop).
- **Zoom Prevention & Mobile Support:** Native `touch-action` and gesture handlers preventing mobile/desktop pinch zoom while maintaining smooth scrolling.

*(An optional legacy Streamlit prototype is preserved under `frontend/app.py` for comparative reference).*

---

## Project Structure

```text
ai-research-system/
│
├── backend/
│   ├── main.py                # FastAPI entrypoint, Jinja2 template & static assets mounting
│   ├── entrypoint.sh          # Container runner (FastMCP background + FastAPI foreground)
│   ├── .env / .env.example
│   │
│   ├── src/
│   │   ├── auth.py            # JWT token creation and verification
│   │   ├── config.py          # Pydantic BaseSettings, model overrides & LangSmith config
│   │   ├── logging.py         # Structured JSON logging
│   │   ├── metrics.py         # Prometheus histogram and counter metrics
│   │   │
│   │   ├── pipeline/
│   │   │   ├── state.py       # ResearchState TypedDict
│   │   │   ├── agents.py      # LLM, prompts, structured chains, and tool-calling agent builders
│   │   │   ├── graph.py       # LangGraph DAG definition, conditional routing & MCP client cache
│   │   │   ├── pipeline.py    # graph.ainvoke() orchestrator
│   │   │   └── utils.py       # Thinking tag stripping & token summation helpers
│   │   │
│   │   └── mcp_server/
│   │       ├── server.py      # FastMCP tool server on port 8001
│   │       └── tools_impl.py  # web_search, scrape_url, arxiv_search, calculator
│   │
│   └── api/
│       ├── routes_auth.py     # /auth/token endpoint
│       └── routes_research.py # /research/run endpoint
│
├── frontend/
│   ├── templates/
│   │   └── index.html         # Jinja2 production single-page application (Screens 0, 1, 2)
│   ├── static/
│   │   ├── css/style.css      # Scholar-Tech design system & cosmic particle styling
│   │   └── js/app.js          # Pure ES6+ client state, auth, history, and marked.js rendering
│   ├── app.py                 # Legacy Streamlit prototype
│   └── requirements.txt
│
├── tests/
│   ├── test_auth.py           # JWT auth and invalid credentials tests
│   └── test_research.py       # Pipeline execution, token guards, and clarification tests
│
├── monitoring/
│   └── prometheus.yml
│
├── conftest.py                # Test client and mock pipeline fixtures
├── Dockerfile                 # Multi-stage build for unified deployment
├── pyproject.toml
└── README.md
```

---

## Installation & Setup

### Prerequisites
- Python 3.13+
- [uv](https://docs.astral.sh/uv/) package manager

### Clone & Install
```bash
git clone https://github.com/<your-username>/ai-research-system.git
cd ai-research-system
uv sync
```

### Environment Variables

Create a `.env` file in the root or `backend/` directory (template provided in `.env.example`):

```ini
JWT_SECRET_KEY=your_long_random_secret_string
TAVILY_API_KEY=your_tavily_api_key_here

OPENAI_API_KEY=your_openai_api_key_here
# Optional model override (defaults to gpt-5-nano)
OPENAI_MODEL=gpt-5-nano

# Database Persistence (Supabase PostgreSQL / Cloud Postgres / Local SQLite)
# Defaults to sqlite:///./research.db if omitted
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres

# FastMCP tool server configuration
MCP_SERVER_URL=http://localhost:8001/mcp
MCP_HOST=0.0.0.0
MCP_PORT=8001

# Optional — LangSmith tracing
LANGCHAIN_TRACING_V2=false
LANGCHAIN_API_KEY=
LANGCHAIN_PROJECT=researchmind
```

---

## How to Run

Two processes (or single container via Docker):

```bash
# terminal 1 — MCP tool server
cd backend
uv run python -m src.mcp_server.server

# terminal 2 — orchestrator
cd backend
uv run uvicorn main:app --reload
```

```bash
# frontend
cd frontend
uv run streamlit run app.py
```

---

## Evaluation Harness (Planned)

Not yet implemented — designed but not built. The plan: a 100-query synthetic evaluation harness scored with hand-rolled LLM-as-judge metrics (over the RAGAS library, since RAGAS's retrieval-focused metrics fit a classic RAG system better than this project's multi-agent architecture):

- **Faithfulness** — reuse the citation verifier: fraction of claims marked fully supported
- **Answer relevancy** — does the report actually address the question asked
- **Context precision** — what fraction of retrieved research content was relevant

Deferred since running 100 full pipeline executions has a real OpenAI cost — to be built once that's worth spending on.

---

## Testing

```bash
uv run pytest
```

Uses `httpx` with `ASGITransport` to test FastAPI endpoints in-process. The `mock_pipeline` fixture patches `run_research_pipeline` so tests never call any external API.

---

## Deployment Architecture

- **Unified Web & Pipeline Container:** Built via a multi-stage `Dockerfile` and hosted on Render.
- **Entrypoint Process Orchestration:** [`backend/entrypoint.sh`](backend/entrypoint.sh) boots the FastMCP tool server in the background on port `8001`, then launches the FastAPI application on `${PORT:-8000}`.
- **Internal Tool Communication:** FastAPI nodes communicate with the FastMCP server over `http://localhost:8001/mcp` within the container's isolated local network.
- **Frontend Serving:** FastAPI serves the Jinja2 single-page application at `/` and static assets from `/static`, requiring no separate frontend hosting service.
- **Custom Domain Ready:** Pre-configured for apex or subdomain deployment (e.g. `madhavmakwana.dev` or `research.madhavmakwana.dev`) with automated SSL certificates.

---

## Observability

- **Prometheus** — `/metrics` endpoint via `prometheus-fastapi-instrumentator`; custom histograms per pipeline step (plan, research, write, critique, verify)
- **LangSmith** (optional) — full trace visualization of every node, tool call, and critic iteration when `LANGCHAIN_TRACING_V2=true`
- **Structured JSON logging** — every run tagged with a `request_id` for trace correlation

---

## Current Limitations & Tradeoffs

- **No production hardening yet** — no wall-clock timeout per run, no graceful degradation if one parallel research branch fails; deferred as a future pass
- **Eval harness not yet built** — `CRITIC_THRESHOLD` is a placeholder until it exists and has been run
- **Frontend has no streaming** — results render only after the full graph completes
- **Verification is costlier and slower** — the verifier's independent tool-calling pass adds a full agentic round trip to every run

---

## Future Improvements

- Wall-clock timeout per run
- Graceful degradation on parallel-branch failure
- Extend test suite to cover graph node routing and MCP tool calls directly
- OpenTelemetry distributed tracing across graph nodes, especially the parallel fan-out branches
- Streaming intermediate pipeline state to the frontend
- Build and run the 100-query eval harness once comfortable with the associated OpenAI cost

---

## Tech Stack

### Backend & Agentic Engine
- Python 3.13, FastAPI, Uvicorn
- LangGraph (`StateGraph`, `Send` parallel fan-out API)
- Model Context Protocol (`mcp`, `langchain-mcp-adapters`, FastMCP)
- OpenAI API (LLM, reasoning model support), Tavily Search API, arXiv API
- BeautifulSoup4
- Prometheus + prometheus-fastapi-instrumentator
- LangSmith (optional tracing)
- JWT authentication (python-jose)
- Structured JSON logging (python-json-logger)
- uv package manager

### Frontend
- Pure Vanilla Web (HTML5, CSS3, ES6+ JavaScript)
- Jinja2 Server-Side Templating
- Marked.js (client-side markdown parsing)
- Scholar-Tech Obsidian/Solar-Amber Custom Design System

### Testing
- pytest + pytest-anyio, httpx with ASGITransport, unittest.mock

### Deployment
- Multi-stage Docker, Render container hosting, shell process supervisor