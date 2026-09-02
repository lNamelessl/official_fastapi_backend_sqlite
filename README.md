# FastAPI Backend SQLite — Railway Template

A backend-only version of the [official Full Stack FastAPI Template](https://github.com/tiangolo/full-stack-fastapi-template), adapted for **SQLite** and **one-click deployment on [Railway](https://railway.com)** — no frontend, no PostgreSQL, no external database service.

[![Test Backend](../../actions/workflows/test-backend.yml/badge.svg)](../../actions/workflows/test-backend.yml)

[![Deploy on Railway](https://railway.com/button.svg)](https://railway.app/new?github_url=https://github.com/lNamelessl/official_fastapi_backend_sqlite)

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

**One-click deploy to Railway**: click the **Deploy on Railway** button above. Railway builds the Docker image, sets a `DATABASE_URL` for SQLite, and starts the app — migrations and the first superuser are created automatically at startup.

Or clone the repository and deploy from your own GitHub account with:

```
https://railway.app/new?github_url=<your-repo-url>
```

## Deploying to Railway

The repository ships with a root-level `Dockerfile` and a `railway.json` so Railway (and the Railway CLI's `railway up`) builds and runs it without extra configuration:

1. The Docker image installs dependencies with `uv`, applies Alembic migrations, seeds the first superuser (`scripts/prestart.sh`), and starts FastAPI bound to Railway's `PORT` (`${PORT:-8000}` locally).
2. The `railway.json` deploy step points the healthcheck at the redirect-free `/health` endpoint and restarts on failure.

Environment variables to set on the Railway service:

* `PROJECT_NAME` — shown in the API docs and emails.
* `SECRET_KEY` — generate with `openssl rand -hex 32`.
* `FIRST_SUPERUSER` — email of the initial admin.
* `FIRST_SUPERUSER_PASSWORD` — generate a strong one; it is used to seed the superuser on first boot.
* `DATABASE_URL` *(optional)* — where the SQLite file lives. Accepts a `sqlite:///...` URL or a bare path. To survive redeploys, attach a Railway volume (e.g. mount at `/data`) and set `DATABASE_URL=/data/app.db`. Default: `sqlite:///./app.db` inside the container.
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
