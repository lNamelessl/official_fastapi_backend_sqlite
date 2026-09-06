# FastAPI Project - Deployment

## Deploy to Railway

The repository is a one-click Railway template: a root-level `Dockerfile` provides the build, and `railway.json` provides the deploy configuration (start command, healthcheck, restart policy).

### One-Click Deploy

Click the **Deploy on Railway** button in the [README](./README.md), or open <https://railway.com/deploy/official-fastapi-backend-sqlite>.

The deploy form prompts for **nothing**: the service and the `/data` volume are provisioned automatically, and the app generates its `SECRET_KEY` and initial admin password on first boot (persisted next to the database and logged once in the deploy logs). To deploy your own fork instead, open:

```
https://railway.app/new?github_url=<your-repo-url>
```

### Deploy With the Railway CLI

```bash
npm i -g @railway/cli
railway login
railway init --name my-project
railway up
```

`railway up` builds the root `Dockerfile` and applies the deploy settings from `railway.json`.

### Environment Variables

No variables are required: on first boot the app generates a `SECRET_KEY` and an initial admin password (persisted next to the database file and logged once), and seeds the superuser `admin@example.com`.

Optional overrides you can set on the service (dashboard or `railway variables`):

* `PROJECT_NAME`: The name of the project, used in the API documentation and emails (default: `FastAPI Backend SQLite`).
* `SECRET_KEY`: A secret key used to sign security tokens; generated and persisted on the volume when unset.
* `FIRST_SUPERUSER`: The email address of the first superuser (default: `admin@example.com`).
* `FIRST_SUPERUSER_PASSWORD`: The password of the first superuser; generated, persisted, and logged once when unset. If you generate your own, use `openssl rand -hex 32`.
* `DATABASE_URL`: Where the SQLite database file lives. Accepts a `sqlite:///...` SQLAlchemy URL or a bare file path; the Docker image defaults to `/data/app.db`.
* `FRONTEND_HOST`: The origin allowed by CORS (e.g. your generated Railway domain).
* `SMTP_HOST`, `SMTP_USER`, `SMTP_PASSWORD`, `EMAILS_FROM_EMAIL`: Enable transactional emails with your SMTP provider.
* `SENTRY_DSN`: Enable Sentry error tracking.

Do **not** set `FASTAPI_ENV`: the setting only accepts `"development"`, and leaving it unset enables strict validation of default secrets at boot.

### Persist the Database

SQLite lives in a single file, so attach a Railway volume to keep it across deploys:

1. In the Railway dashboard, add a volume to the service mounted at `/data` (or `railway volume add --mount-path /data`).
2. Set `DATABASE_URL=/data/app.db`.

On every boot the container runs `scripts/prestart.sh`, which applies Alembic migrations and creates the first superuser if it does not exist, then starts the API.

### Domain and Healthcheck

Generate a public domain from the dashboard (or `railway domain`). Railway probes the `/health` endpoint configured in `railway.json` — it is redirect-free at the root level, so the healthcheck cannot be tripped by FastAPI's 307 redirects.

## Self-Host With Docker Compose

For deployment to your own server:

```bash
PROJECT_NAME="My API" \
SECRET_KEY="$(openssl rand -hex 32)" \
FIRST_SUPERUSER=admin@example.com \
FIRST_SUPERUSER_PASSWORD="$(openssl rand -hex 16)" \
docker compose up -d --build --wait
```

The SQLite file is persisted in the `app-db-data` volume mounted at `/data`.
