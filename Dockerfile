FROM python:3.13-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

FROM python:3.13-slim

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY backend/ ./
COPY frontend/ ./frontend/

ENV PATH="/app/.venv/bin:$PATH"

RUN chmod +x entrypoint.sh

EXPOSE 8000
EXPOSE 8001

CMD ["/bin/sh", "entrypoint.sh"]