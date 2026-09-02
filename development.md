# FastAPI Project - Development

## Local Development

The backend uses SQLite, so no supporting services are needed.

From the `backend` directory, install the dependencies and prepare the database:

```bash
uv sync
uv run bash scripts/prestart.sh
```

Start the FastAPI development server:

```bash
uv run fastapi dev
```

Now you can open these URLs:

Backend API: <http://localhost:8000>

Automatic interactive API documentation with Swagger UI: <http://localhost:8000/docs>

The database file is created at `backend/app.db` by default (configured in the root `.env` as `DATABASE_URL=sqlite:///./app.db`). You can point it anywhere — a bare path like `DATABASE_URL=/data/app.db` works too.

## Full Stack with Docker Compose

To run the backend in Docker Compose with the SQLite file persisted in a volume:

```bash
docker compose up -d --build --wait
```

Now you can open these URLs:

Backend API: <http://localhost:8000>

Automatic interactive API documentation with Swagger UI: <http://localhost:8000/docs>

The Compose stack mounts a named volume at `/data` and sets `DATABASE_URL=/data/app.db`, so the database survives container recreation. To monitor it, use `docker compose logs`, or `docker compose logs backend` for the backend service.

## The `.env` File

The tracked `.env` file contains local development defaults, passwords, and other configuration.

Do not store deployment secrets in `.env`. Configure them in your platform (e.g. the Railway dashboard) as described in the [deployment guide](./deployment.md).

## Pre-commit Hooks and Code Linting

The project uses [prek](https://prek.j178.dev/), a modern alternative to [pre-commit](https://pre-commit.com/), for code linting and formatting.

You can find a file `.pre-commit-config.yaml` with configurations at the root of the project.

### Install `prek` to Run Automatically

`prek` is already part of the dependencies of the project.

From the project root, install the Git hook so that `prek` runs automatically before each commit:

```bash
uv run prek install -f
```

The `-f` flag forces the installation, in case there was already a `pre-commit` hook previously installed.

Now whenever you try to commit, for example with:

```bash
git commit
```

`prek` will check and format the code you are about to commit. If it modifies any files, add those files to Git again before committing.

### Run `prek` Manually

You can also run `prek` manually on all files from the project root:

```bash
uv run prek run --all-files
```
