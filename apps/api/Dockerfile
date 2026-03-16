FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

WORKDIR /app

COPY apps/api/pyproject.toml /app/pyproject.toml
RUN uv sync --no-dev

COPY apps/api /app
COPY arena /arena
COPY knowledge /knowledge
COPY evals /evals
COPY packages/contracts /packages/contracts

CMD ["uv", "run", "uvicorn", "devprod_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
