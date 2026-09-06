# FastAPI Backend SQLite — Railway Template

A backend-only version of the [official Full Stack FastAPI Template](https://github.com/tiangolo/full-stack-fastapi-template), adapted for **SQLite** and **one-click deployment on [Railway](https://railway.com)** — no frontend, no PostgreSQL, no external database service.

[![Test Backend](../../actions/workflows/test-backend.yml/badge.svg)](../../actions/workflows/test-backend.yml)

[![Deploy on Railway](https://railway.com/button.svg)](https://railway.com/deploy/official-fastapi-backend-sqlite)

## Technology Stack and Features

- ⚡ [**FastAPI**](https://fastapi.tiangolo.com) for the Python backend API.
  - 🧰 [SQLModel](https://sqlmodel.tiangolo.com) for the Python SQL database interactions (ORM).
  - 🔍 [Pydantic](https://docs.pydantic.dev), used by FastAPI, for the data validation and settings management.
  - 💾 **SQLite** as the SQL database — a single file, zero infrastructure.
- 🚢 **Railway-ready**: `railway.json` config-as-code, `$PORT` binding, healthchecks, and automatic migrations on every deploy.
- 🐋 [Docker Compose](https://www.docker.com) for local runs with a persistent SQLite volume.
- 🔒 Secure password hashing by default.
- 🔑 JWT (JSON Web Token) authentication.
- 📫 Email-based password recovery (optional, needs an SMTP provider).
- ✅ Tests with [Pytest](https://pytest.org).
- 🏭 CI based on GitHub Actions.

## How To Use It

**One-click deploy to Railway**: click the **Deploy on Railway** button above (marketplace URL: <https://railway.com/deploy/official-fastapi-backend-sqlite>). The deploy form prompts for **nothing** — Railway provisions the `backend` service plus a volume at `/data` and starts the app.

On first boot the app:

1. Applies Alembic migrations to the SQLite database on the volume.
2. Generates a `SECRET_KEY` and an initial admin password, and persists both in `.bootstrap_secrets.json` next to the database file (so they survive restarts).
3. Seeds the superuser `admin@example.com` with the generated password and logs it once — search the deploy logs for "Generated initial admin password" (or read the file from the volume), then sign in and change the password via the API.

Optional overrides you can set later as service variables: `PROJECT_NAME`, `FIRST_SUPERUSER`, `FIRST_SUPERUSER_PASSWORD`, `DATABASE_URL`, `FRONTEND_HOST` (CORS origin), and SMTP settings for emails.

## Deploying to Railway

The repository ships with a root-level `Dockerfile` and a `railway.json` so Railway (and the Railway CLI's `railway up`) builds and runs it without extra configuration:

1. The Docker image installs dependencies with `uv`, applies Alembic migrations, seeds the first superuser (`scripts/prestart.sh`), and starts FastAPI bound to Railway's `PORT` (`${PORT:-8000}` locally).
2. The `railway.json` deploy step points the healthcheck at the redirect-free `/health` endpoint and restarts on failure.

All credentials are generated on first boot when not provided, so the deployment needs zero variables. Optional environment variables:

* `PROJECT_NAME` — shown in the API docs and emails (default: `FastAPI Backend SQLite`).
* `SECRET_KEY` — JWT signing key; generated and persisted on the volume when unset.
* `FIRST_SUPERUSER` — email of the initial admin (default: `admin@example.com`).
* `FIRST_SUPERUSER_PASSWORD` — generated, persisted, and logged once when unset.
* `DATABASE_URL` *(optional)* — where the SQLite file lives. Accepts a `sqlite:///...` URL or a bare path; the Docker image defaults to `/data/app.db` on the volume.
* `FRONTEND_HOST` *(optional)* — origin allowed by CORS, e.g. your generated `https://<project>.up.railway.app` domain.

Do **not** set `FASTAPI_ENV` in production — leaving it unset enables strict validation of default secrets.

After the first deploy, generate a public domain in the Railway dashboard (or `railway domain` with the CLI) and point a browser at `/docs` for the interactive API documentation.

## Backend Development

Backend docs: [backend/README.md](./backend/README.md).

## Deployment

Railway deployment details and self-hosting with Docker Compose: [deployment.md](./deployment.md).

## Development

General development docs: [development.md](./development.md).

## License

Based on the Full Stack FastAPI Template, licensed under the terms of the MIT license.
