FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

WORKDIR /app

COPY apps/api/pyproject.toml /app/pyproject.toml
COPY apps/api/uv.lock /app/uv.lock
RUN uv sync --no-dev --no-install-project

COPY apps/api /app
COPY arena /arena
COPY knowledge /knowledge
COPY evals /evals
COPY packages/contracts /packages/contracts
RUN uv sync --no-dev

CMD ["uv", "run", "uvicorn", "devprod_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
