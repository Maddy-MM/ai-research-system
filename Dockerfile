# ---------------------------------------------------------------------------
# Stage 1 — dependency installation
# Using a separate stage keeps the final image clean.
# If your dependencies don't change, Docker cache means this stage
# is skipped on rebuilds — making builds much faster.
# ---------------------------------------------------------------------------
FROM python:3.13-slim AS builder

# Install uv — the same package manager you use locally
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copy dependency files first (before source code).
# Docker builds layers in order — if only your source code changes,
# the dependency installation layer is reused from cache.
COPY pyproject.toml uv.lock ./

# Install dependencies into /app/.venv
# --frozen        : use exact versions from uv.lock, never resolve
# --no-dev        : skip dev/test dependencies in production
RUN uv sync --frozen --no-dev


# ---------------------------------------------------------------------------
# Stage 2 — final image
# Start fresh from slim, copy only what's needed from builder.
# This means build tools, uv itself, and caches don't end up in production.
# ---------------------------------------------------------------------------
FROM python:3.13-slim

WORKDIR /app

# Copy the virtual environment from the builder stage
COPY --from=builder /app/.venv /app/.venv

# Copy application source code
COPY backend/ ./


# Make sure Python uses the venv we installed into
ENV PATH="/app/.venv/bin:$PATH"

# Document which port the app listens on (doesn't actually publish it —
# that's done with -p at docker run time or in docker-compose)
EXPOSE 8000


# Start the app with uvicorn
# --host 0.0.0.0    : listen on all interfaces (not just localhost inside container)
# --port 8000       : match EXPOSE above
# --workers 1       : single worker is correct for async FastAPI with LLM calls
#                     (multiple workers would each hold their own model state)
CMD ["/app/.venv/bin/uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]