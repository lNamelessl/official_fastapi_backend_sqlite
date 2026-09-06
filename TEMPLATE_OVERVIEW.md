# FastAPI Backend SQLite — Railway Template

A backend-only version of the [official Full Stack FastAPI Template](https://github.com/tiangolo/full-stack-fastapi-template) by tiangolo, adapted for **SQLite** and packaged for **one-click deployment on Railway** — no frontend, no PostgreSQL server, no external database service, and **zero environment variables to fill in before deploying**.

[![Deploy on Railway](https://railway.com/button.svg)](https://railway.com/deploy/official-fastapi-backend-sqlite)

## What You Get

- ⚡ [FastAPI](https://fastapi.tiangolo.com) with automatic interactive API docs at `/docs`.
- 🧰 [SQLModel](https://sqlmodel.tiangolo.com) ORM + Alembic migrations.
- 💾 **SQLite** — the database is a single file on a Railway volume (`/data/app.db`), so there is nothing extra to run, back up, or pay for.
- 🔑 JWT authentication with secure password hashing (argon2).
- 🤖 **Zero-config bootstrap**: on first boot the app generates its own `SECRET_KEY` and initial admin password (persisted on the volume), applies migrations, and seeds the admin — the deploy form has nothing to fill in.
- 🩺 A redirect-free `/health` endpoint wired into the Railway healthcheck, plus restart-on-failure policy.
- 🔧 `$PORT` binding so the app works on Railway's dynamic port routing out of the box.

## How It Deploys

The repository ships a root-level `Dockerfile` (fixed for Railway's builders — no BuildKit bind mounts) and a `railway.json` with the builder, start command, healthcheck path, and restart policy. Railway builds the image from this repo, attaches a volume at `/data`, and starts the container: `prestart.sh` runs `alembic upgrade head` and seeds the superuser, then FastAPI serves on `$PORT`. No variables are required — everything sensitive is generated per deployment.

# Deploy and Host

Deploy the FastAPI + SQLite backend template on Railway with the **Deploy on Railway** button above. One service is provisioned (the `backend` API container) together with a volume for the SQLite file, and the deploy form prompts for **nothing** — hit deploy and the API comes up fully configured.

## About Hosting

Hosting this template means running a single stateless API container plus one persistent volume:

- **Services provisioned:** one `backend` service (Dockerfile build) and one volume mounted at `/data` for the SQLite database file. No database server, cache, or reverse proxy services are needed.
- **Variables:** none required. On first boot the app generates a `SECRET_KEY` and an initial admin password, persists them in `.bootstrap_secrets.json` next to the database file on the volume, logs the generated admin password once in the deploy logs, and creates the superuser `admin@example.com`.
- **After deploying:** open the deploy logs (or read `.bootstrap_secrets.json` from the volume) to retrieve the initial admin password, sign in at `/docs` via the `login/access-token` endpoint, and change the password through the API. Optional overrides you may set later: `PROJECT_NAME`, `FIRST_SUPERUSER`, `FIRST_SUPERUSER_PASSWORD`, `DATABASE_URL` (e.g. a different volume path), `FRONTEND_HOST` (CORS origin), and SMTP settings for emails.
- Do **not** set `FASTAPI_ENV` in production — leaving it unset enables strict validation of default secrets at boot.

## Why Deploy

- **Truly one click.** No deploy-form fields, no secret generation on your side, no database connection strings — and because the bootstrap is baked into the image, `railway up` and GitHub-triggered deploys behave identically to the marketplace deploy.
- **Zero database operations.** SQLite removes the Postgres service entirely: no credentials to rotate, no database backups to configure for small apps — the whole database is one file on your volume.
- **Faithful to the official template.** This is tiangolo's full-stack-fastapi-template backend with its battle-tested auth, CRUD, and email flows — not a from-scratch scaffold — with only the frontend and PostgreSQL layers removed.
- **Correct Railway behavior baked in.** The official template's Dockerfile fails on Railway's builders (BuildKit bind mounts) and its healthcheck trips FastAPI 307 redirects; this fork fixes both, binds to `$PORT`, and runs migrations in the container start command.

## Common Use Cases

- REST APIs for mobile apps, SPAs, and integrations that need real auth (JWT + superuser roles) without operating a database server.
- Internal tools and admin backends where a single-file SQLite database is plenty and simplicity beats horizontal scale.
- Rapid prototyping of FastAPI projects on the official template's conventions (SQLModel, Alembic, Pydantic settings) with one-click hosting.
- Self-hosted personal APIs — hobby projects, webhooks, small SaaS backends — that should cost one service plus one volume.

## Dependencies for

### Deployment Dependencies

- A Railway account (Hobby plan or trial). No external database dependency: the SQLite file lives on the attached Railway volume at `/data`.
- Post-deploy step: retrieve the generated admin password from the deploy logs (search for "Generated initial admin password") or from `.bootstrap_secrets.json` on the volume, then sign in and change it via the API. Verify the deployment with `GET /health` (expect `200`) and a `POST /api/v1/login/access-token` call.
- Optional: an SMTP provider (`SMTP_HOST`, `SMTP_USER`, `SMTP_PASSWORD`, `EMAILS_FROM_EMAIL`) if you want password-reset and test emails delivered; without it, email endpoints are disabled.
- Optional: a Sentry DSN (`SENTRY_DSN`) for error tracking.

## Local Development

```bash
uv sync
uv run bash scripts/prestart.sh
uv run fastapi dev
```

See [development.md](./development.md) and [deployment.md](./deployment.md).
