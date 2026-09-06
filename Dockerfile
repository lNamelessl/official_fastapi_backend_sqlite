FROM python:3.14

ENV PYTHONUNBUFFERED=1

# Install uv
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#installing-uv
COPY --from=ghcr.io/astral-sh/uv:0.9.26 /uv /uvx /bin/

# Compile bytecode
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#compiling-bytecode
ENV UV_COMPILE_BYTECODE=1

# uv Cache
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#caching
ENV UV_LINK_MODE=copy

WORKDIR /app/

# Place executables in the environment at the front of the path
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#using-the-environment
ENV PATH="/app/.venv/bin:$PATH"

# Default the SQLite file to the volume mount point used by Railway
# deployments (the directory is created on boot; override with DATABASE_URL).
ENV DATABASE_URL=/data/app.db

# Install dependencies. Plain COPY layers instead of BuildKit bind mounts,
# which Railway's builders reject.
COPY pyproject.toml uv.lock /app/
COPY backend/pyproject.toml backend/alembic.ini /app/backend/

RUN uv sync --frozen --no-install-workspace --package app

COPY ./backend/scripts /app/backend/scripts

COPY ./backend/app /app/backend/app

# Sync the project
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#intermediate-layers
RUN uv sync --frozen --package app

WORKDIR /app/backend/

# Migrations and seed data must run at container start (platforms like Railway
# don't reliably support preDeployCommand), then serve on the injected PORT.
CMD ["sh", "-c", "bash scripts/prestart.sh && exec fastapi run --host 0.0.0.0 --port ${PORT:-8000} --workers 4"]
