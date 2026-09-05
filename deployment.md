# FastAPI Project - Deployment

## Deploy to Railway

The repository is a one-click Railway template: a root-level `Dockerfile` provides the build, and `railway.json` provides the deploy configuration (start command, healthcheck, restart policy).

### One-Click Deploy

Click the **Deploy on Railway** button in the [README](./README.md), or open <https://railway.com/deploy/official-fastapi-backend-sqlite>.

The deploy form prompts for the five template variables (`PROJECT_NAME`, `SECRET_KEY`, `FIRST_SUPERUSER`, `FIRST_SUPERUSER_PASSWORD`, and `DATABASE_URL` — enter `/data/app.db`). To deploy your own fork instead, open:

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

Add these required variables to the service (dashboard or `railway variables --set ...`):

* `PROJECT_NAME`: The name of the project, used in the API documentation and emails.
* `SECRET_KEY`: A secret key used to sign security tokens.
* `FIRST_SUPERUSER`: The email address of the first superuser.
* `FIRST_SUPERUSER_PASSWORD`: The password of the first superuser.

You can generate secure values for `SECRET_KEY` and `FIRST_SUPERUSER_PASSWORD` with:

```bash
openssl rand -hex 32
```

Optional variables:

* `DATABASE_URL`: Where the SQLite database file lives. Accepts a `sqlite:///...` SQLAlchemy URL or a bare file path (`/data/app.db`). Defaults to `sqlite:///./app.db` inside the container.
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
