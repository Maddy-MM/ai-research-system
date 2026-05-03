# ResearchMind

  

A **multi-agent AI research pipeline** that takes any topic and autonomously searches the web, scrapes top sources, writes a structured report, and critiques it — all in a single pipeline run.

  

---

  

## Table of Contents

  

1. Overview

2. Features

3. Project Workflow

4. Pipeline Architecture

5. Authentication

6. API Endpoints

7. Frontend

8. Project Structure

9. Installation & Setup

10. How to Run

11. Testing

12. Deployment Architecture

13. Observability

14. Current Limitations & Tradeoffs

15. Future Improvements

16. Tech Stack

  

---

  

## Overview

  

ResearchMind implements an **end-to-end agentic research pipeline** with a production-grade backend:

  

- **FastAPI backend** orchestrates four pipeline steps with JWT auth, structured JSON logging, and Prometheus metrics

- **Streamlit frontend** provides a JWT-authenticated research interface with a dedicated results screen

- Components are independently deployable

  

The system uses **LangChain agents** backed by Groq-hosted LLMs to reason over real-time web data and produce structured, critiqued research reports.

  

---

  

## Live Demo

  

- **Backend API:** [ResearchMind - Backend (Render)](https://your-backend.onrender.com)

- **Frontend:** [ResearchMind - Frontend (Streamlit)](https://your-frontend.streamlit.app)

  

> **Note:** The backend is hosted on Render's free tier and may take 30–60 seconds to wake up on the first request.

  

**Demo credentials:**

  

- Username: `admin`

- Password: `admin123`

  

---

  

## Features

  

- JWT-authenticated access — login required before using the app

- Four-step agentic pipeline: search → scrape → write → critique

- Real-time web search via Tavily API

- Intelligent URL scraping with BeautifulSoup

- Structured research reports with introduction, key findings, conclusion, and sources

- Scored critic feedback on every report

- Prometheus metrics for pipeline observability

- Structured JSON logging across all backend components

- Streamlit UI with custom dark theme and ResearchMind branding

- Separate results screen — report and feedback rendered on a clean dedicated view

- Modular API-based backend

- Docker support for deployment

- Full async test suite with mocked pipeline

  

---

  

## Project Workflow

  

1. User logs in with username and password

2. JWT token issued and stored for the session

3. User enters a research topic

4. Search Agent queries Tavily for recent, reliable sources

5. Reader Agent scrapes the most relevant URL for deeper content

6. Writer Chain drafts a structured research report

7. Critic Chain reviews and scores the report

8. Results rendered on a dedicated screen with download option

  

---

  

## Pipeline Architecture

  

### Step 1 — Search Agent

  

- LangChain agent backed by `meta-llama/llama-4-scout-17b-16e-instruct` via Groq

- Uses the `web_search` tool powered by Tavily (`max_results=3`)

- Returns titles, URLs, and snippets for the most relevant sources

  

### Step 2 — Reader Agent

  

- Separate LangChain agent with the `scrape_url` tool

- Selects the most relevant URL from search results and scrapes clean text

- BeautifulSoup strips scripts, styles, nav, and footer elements

- Content capped at 3000 characters to stay within context limits

  

### Step 3 — Writer Chain

  

- LangChain chain (prompt → LLM → output parser), no tool use

- Combines search snippets and scraped content as research context

- Produces a structured report: Introduction, Key Findings (min. 3 points), Conclusion, Sources

  

### Step 4 — Critic Chain

  

- Separate chain that reviews the report strictly

- Returns a fixed format: Score, Strengths, Areas to Improve, One-line verdict

  

---

  

## Authentication

  

ResearchMind uses **JWT-based authentication**. A login is required before accessing any part of the application.

  

- Passwords are verified against a hardcoded admin user configured via environment variables

- On login, the backend issues a signed JWT token

- All protected endpoints verify the token via a FastAPI `HTTPBearer` dependency

  

**Public endpoints:** `/health`, `/auth/token`

  

**Protected endpoints:** `/research/run`

  

---

  

## API Endpoints

  

### Health Check

  

`GET /health` — Returns `{"status": "ok"}`. Used for liveness probes and uptime monitoring.

  

### Login

  

`POST /auth/token` — Accepts form data `username` and `password`. Returns a signed JWT `access_token` on success, HTTP 401 on invalid credentials.

  

### Run Pipeline

  

`POST /research/run` _(protected)_ — Accepts JSON `{"topic": "..."}`. Runs all four pipeline steps and returns:

  

```json

{

  "request_id": "uuid",

  "topic": "...",

  "report": "...",

  "feedback": "..."

}

```

  

---

  

## Frontend

  

Built with Streamlit:

  

- Login screen with JWT authentication — centered layout, orange branding, separate from the main app

- Main screen with topic input, run button, and four pipeline step cards

- Loading screen with pipeline status messages while the backend runs

- Results screen — report and critic feedback rendered on a completely separate view

- Download button to save the report as a Markdown file

- New Research button to return to the main screen

- Sign Out button in sidebar

  

### User Flow

  

1. Sign in with username and password

2. Enter a research topic and click Run

3. Watch the pipeline status while agents work

4. Read the report and critic feedback on the results screen

5. Download the report or start a new research

  

---

  

## Project Structure

  

```text
ai-research-system/
│
├── backend/
│   ├── main.py
│   ├── .env
│   ├── .env.example
│   │
│   ├── src/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── config.py
│   │   ├── logging.py
│   │   ├── metrics.py
│   │   │
│   │   └── pipeline/
│   │       ├── __init__.py
│   │       ├── tools.py
│   │       ├── agents.py
│   │       └── pipeline.py
│   │
│   └── api/
│       ├── __init__.py
│       ├── routes_auth.py
│       └── routes_research.py
│
├── frontend/
│   ├── app.py
│   ├── requirements.txt
│   └── .streamlit/
│       └── config.toml
│
├── tests/
│   ├── test_auth.py
│   └── test_research.py
│
├── monitoring/
│   └── prometheus.yml
│
├── conftest.py
├── Dockerfile
├── pytest.ini
├── pyproject.toml
├── uv.lock
├── .python-version
├── .gitignore
└── README.md
```

  

---

  

## Installation & Setup

  

### Prerequisites

  

- Python 3.13+

- [uv](https://docs.astral.sh/uv/) package manager

  

### Clone Repository

  

```bash

git clone https://github.com/<your-username>/ai-research-system.git

cd ai-research-system

```

  

### Install Dependencies

  

```bash

uv sync

```

  

### Frontend Dependencies

Streamlit Cloud requires a `requirements.txt` in the `frontend/` directory. This contains only `streamlit` and `requests` — all backend dependencies are managed separately via `pyproject.toml` and uv.

### Environment Variables

  

Create a `.env` file in the `backend/` directory:

  

```ini

JWT_SECRET_KEY=your_long_random_secret_string

TAVILY_API_KEY=your_tavily_api_key_here

GROQ_API_KEY=your_groq_api_key_here

```

  

> See `.env.example` for the full template.

  

---

  

## How to Run

  

### Backend

  

```bash

cd backend

uvicorn main:app --reload

```

  

### Frontend

  

```bash

cd frontend

streamlit run app.py

```

  

> Set `API_URL` in `frontend/app.py` to switch between local and deployed backend:

>

> ```python

> API_URL = "http://127.0.0.1:8000"           # local

> API_URL = "https://your-backend.onrender.com"  # production

> ```

  

---

  

## Testing

  

```bash

pytest

```

  

The test suite uses `httpx` with `ASGITransport` to test FastAPI endpoints in-process — no real network calls. The `mock_pipeline` fixture patches `run_research_pipeline` so tests never call Tavily, Groq, or BeautifulSoup.

  

```bash

pytest -v                  # verbose output

pytest tests/test_auth.py  # auth tests only

```

  

---

  

## Deployment Architecture

  

- Backend deployed as a Dockerized FastAPI service on Render

- Frontend deployed separately on Streamlit Community Cloud

- Communication via REST APIs with JWT Bearer token authentication

- Environment variables managed via Render dashboard and Streamlit secrets

  

---

  

## Observability

  

### Prometheus

  

- `prometheus-fastapi-instrumentator` auto-instruments all HTTP routes

- `/metrics` endpoint exposes request counts, latencies, and pipeline step durations

- Custom metrics:

  - `pipeline_requests_total` — counter labelled by status (success/error)

  - `pipeline_duration_seconds` — histogram for total pipeline duration

  - `pipeline_step_duration_seconds` — histogram labelled by step (search, scrape, write, critique)

  

### Grafana

  

- Connect Grafana to the Prometheus instance manually via the `/metrics` endpoint

- No code changes required — all metrics are available as soon as the backend is running

  

### Structured Logging

  

- All backend components use JSON-formatted logs via `python-json-logger`

- Every pipeline run is tagged with a `request_id` for full trace correlation across log lines

  

---

  

## Current Limitations & Tradeoffs

  

- **Synchronous pipeline in async route** — `run_research_pipeline` is sync and runs directly in the async FastAPI route. This works because LLM calls dominate the time, but under high concurrency a thread pool executor would be the correct upgrade

- **Hardcoded admin user** — user credentials are set via environment variables; no user registration or persistent user store

- **No streaming** — the pipeline result is returned as a single response after all four steps complete; streaming step-by-step updates would improve perceived latency

- **Context cap on scraping** — scraped content is limited to 3000 characters to stay within LLM context limits; longer articles are truncated

  

---

  

## Future Improvements

  

- Streaming pipeline updates to the frontend as each step completes

- Persistent report history per user

- Support for multiple URLs scraped in parallel

- Selectable LLM providers (OpenAI, Anthropic, Groq)

- Grafana dashboard template committed to the repo

- CI/CD pipeline with GitHub Actions

- UptimeRobot health monitoring for Render free tier

  

---

  

## Tech Stack

  

### Backend

  

- FastAPI

- LangChain + LangGraph

- Groq Inference API (`meta-llama/llama-4-scout-17b-16e-instruct`)

- Tavily Search API

- BeautifulSoup4

- Prometheus + prometheus-fastapi-instrumentator

- JWT authentication (python-jose, passlib, bcrypt)

- Structured JSON logging (python-json-logger)

- uv package manager

  

### Frontend

  

- Streamlit

- Custom dark theme via `.streamlit/config.toml` — orange accent, deep dark backgrounds

  

### Testing

  

- pytest + pytest-anyio

- httpx with ASGITransport

- unittest.mock for pipeline isolation

  

### Deployment

  

- Docker (backend)

- Render (backend hosting)

- Streamlit Community Cloud (frontend hosting)