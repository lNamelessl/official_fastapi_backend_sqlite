# FastAPI Backend SQLite — Railway Template

A backend-only version of the [official Full Stack FastAPI Template](https://github.com/tiangolo/full-stack-fastapi-template) by tiangolo, adapted for **SQLite** and packaged for **one-click deployment on Railway** — no frontend, no PostgreSQL server, no external database service.

[![Deploy on Railway](https://railway.com/button.svg)](https://railway.app/new?github_url=https://github.com/lNamelessl/official_fastapi_backend_sqlite)

## What You Get

- ⚡ [FastAPI](https://fastapi.tiangolo.com) with automatic interactive API docs at `/docs`.
- 🧰 [SQLModel](https://sqlmodel.tiangolo.com) ORM + Alembic migrations.
- 💾 **SQLite** — the database is a single file on a Railway volume (`/data/app.db`), so there is nothing extra to run, back up, or pay for.
- 🔑 JWT authentication with secure password hashing (argon2).
- 🌱 First-boot automation: migrations are applied and the first superuser is seeded automatically every time the container starts.
- 🩺 A redirect-free `/health` endpoint wired into the Railway healthcheck, plus restart-on-failure policy.
- 🔧 `$PORT` binding so the app works on Railway's dynamic port routing out of the box.

## How It Deploys

The repository ships a root-level `Dockerfile` (fixed for Railway's builders — no BuildKit bind mounts) and a `railway.json` with the builder, start command, healthcheck path, and restart policy. Railway builds the image, attaches a volume at `/data`, and starts the container: `prestart.sh` runs `alembic upgrade head` and seeds the superuser, then FastAPI serves on `$PORT`.

# Deploy and Host

Deploy the FastAPI + SQLite backend template on Railway with the **Deploy on Railway** button above. One service is provisioned (the `backend` API container) together with a volume for the SQLite file, so the database survives redeploys. Migrations and superuser seeding run automatically at every container start — there is no separate migration step to babysit.

## About Hosting

Hosting this template means running a single stateless API container plus one persistent volume:

- **Services provisioned:** one `backend` service (Dockerfile build) and one volume mounted at `/data` for the SQLite database file. No database server, cache, or reverse proxy services are needed.
- **Environment variables to set on the service:**
  - `PROJECT_NAME` — shown in the API docs and emails.
  - `SECRET_KEY` — signs JWTs; generate with `openssl rand -hex 32`.
  - `FIRST_SUPERUSER` — email of the seeded admin.
  - `FIRST_SUPERUSER_PASSWORD` — password of the seeded admin; use a strong generated value.
  - `DATABASE_URL` — already wired to `/data/app.db` on the volume; accepts `sqlite:///...` URLs or bare paths.
  - `FRONTEND_HOST` *(optional)* — CORS origin to allow, e.g. your generated Railway domain.
- Do **not** set `FASTAPI_ENV` in production — leaving it unset enables strict validation of default secrets at boot.

## Why Deploy

- **Zero database operations.** SQLite removes the Postgres service entirely: no connection strings, no credentials to rotate, no database backups to configure for small apps — the whole database is one file on your volume.
- **Faithful to the official template.** This is tiangolo's full-stack-fastapi-template backend with its battle-tested auth, CRUD, and email flows — not a from-scratch scaffold — with only the frontend and PostgreSQL layers removed.
- **Correct Railway behavior baked in.** The official template's Dockerfile fails on Railway's builders (BuildKit bind mounts) and its healthcheck trips FastAPI 307 redirects; this fork fixes both, binds to `$PORT`, and runs migrations in the container start command so CLI and GitHub-triggered deploys behave identically.

## Common Use Cases

- REST APIs for mobile apps, SPAs, and integrations that need real auth (JWT + superuser roles) without operating a database server.
- Internal tools and admin backends where a single-file SQLite database is plenty and simplicity beats horizontal scale.
- Rapid prototyping of FastAPI projects on the official template's conventions (SQLModel, Alembic, Pydantic settings) with one-click hosting.
- Self-hosted personal APIs — hobby projects, webhooks, small SaaS backends — that should cost one service plus one volume.

## Dependencies for

### Deployment Dependencies

- A Railway account (Hobby plan or trial) and a GitHub account to fork or reuse this repository.
- No external database dependency: the SQLite file lives on the attached Railway volume at `/data` (`DATABASE_URL=/data/app.db`).
- Optional: an SMTP provider (`SMTP_HOST`, `SMTP_USER`, `SMTP_PASSWORD`, `EMAILS_FROM_EMAIL`) if you want password-reset and test emails delivered; without it, email endpoints are disabled.
- Optional: a Sentry DSN (`SENTRY_DSN`) for error tracking.
- Post-deploy steps: generate a public domain for the service (dashboard or `railway domain`), then set `FRONTEND_HOST` to that domain so CORS allows your frontend or client origin. Verify with `GET /health` (expect `200`) and a `POST /api/v1/login/access-token` with the seeded superuser.

## Local Development

```bash
uv sync
uv run bash scripts/prestart.sh
uv run fastapi dev
```

See [development.md](./development.md) and [deployment.md](./deployment.md).
