# CMS Milestone 1

This repository contains the Dockerized development skeleton for a role-based CMS. Docker Compose is the canonical runtime: it starts PostgreSQL 18, the Flask API, and the Vite/React frontend together with health checks and source reload.

Milestone 1 deliberately contains no domain schema, authentication, CRUD, uploads, or seed data. Login pages explain that authentication is unavailable, and all dashboard URLs redirect to `/login`.

## Requirements

- Docker Engine with Docker Compose
- Ports `5432`, `5000`, and `5173` available on the host

## Start the stack

The committed defaults work without a local environment file. To customize them:

```sh
cp .env.example .env
```

Then build and start all three services:

```sh
docker compose up --build
```

Open <http://localhost:5173>. The home page calls <http://localhost:5000/api/health> and reports the connection state. PostgreSQL is exposed on `localhost:5432` with the configured `POSTGRES_*` values.

Run in the background, inspect status, and follow logs:

```sh
docker compose up --build -d
docker compose ps
docker compose logs -f
docker compose logs -f backend frontend db
```

Stop containers while keeping the PostgreSQL and `node_modules` volumes:

```sh
docker compose stop
docker compose start
```

Remove containers and the network while retaining volumes:

```sh
docker compose down
```

Only use `docker compose down --volumes` when you intentionally want to erase local PostgreSQL data and the container-managed frontend dependencies.

Rebuild after changing dependencies or Dockerfiles:

```sh
docker compose build --no-cache backend frontend
docker compose up -d
```

## Tests and frontend build

Run all tests in their service containers:

```sh
docker compose exec backend pytest -q backend/tests
docker compose exec frontend npm test
```

Create a production frontend bundle:

```sh
docker compose exec frontend npm run build
```

## Database migrations

The Alembic environment in `migrations/` is tracked, and its `versions/` directory is intentionally empty in Milestone 1. There is no synthetic schema revision.

Apply revisions and inspect migration state:

```sh
docker compose exec backend flask db upgrade
docker compose exec backend flask db current
docker compose exec backend flask db heads
```

When a later milestone introduces reviewed models, create a revision with:

```sh
docker compose exec backend flask db migrate -m "describe schema change"
```

Review the generated revision before applying it. `flask db init` is a one-time maintainer command and must not be run again because the migration environment is already committed.

## Project layout

- `backend/`: Flask application factory, extensions, placeholder Blueprints/models, and pytest suite
- `frontend/`: Vite/React shell, router, inert auth context, API client, placeholders, and Vitest suite
- `migrations/`: tracked Flask-Migrate/Alembic environment
- `compose.yaml`: canonical development runtime and persistent volumes

## Optional host-native troubleshooting

Compose remains the supported workflow. If diagnosing a container-specific issue, equivalent host-native commands are `flask --app backend.app:create_app run --debug` after installing `backend/requirements.txt`, and `npm run dev` from `frontend/` after `npm ci`. A host-native backend needs a host-reachable `DATABASE_URL`, such as `postgresql+psycopg://cms:cms@localhost:5432/cms`.
