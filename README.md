# CMS

This repository contains a Dockerized role-based CMS built with Flask, React, and PostgreSQL. Docker Compose is the canonical runtime: it starts PostgreSQL 18, the Flask API, and the Vite/React frontend together with health checks and source reload.

Milestones 1 and 2 are complete: the repository includes the runnable application skeleton, domain schema and Alembic migration, backend authentication, JWT sessions, numeric role enforcement, Superadmin isolation, rate limits, and frontend login/session restoration.

Milestone 3 is the current implementation target. It adds backend authorization and CRUD for articles, announcements, and pages, including Publisher ownership boundaries and published-only public responses. Taxonomy and user management, media uploads, public content screens, and the complete dashboard remain later work.

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

## Authentication and seed data

The backend exposes these authentication endpoints:

- `POST /api/signup` creates a Visitor with a hashed password.
- `POST /api/login` authenticates Visitor, Publisher, and Admin accounts.
- `POST /api/superadmin-login` is an isolated Superadmin-only login endpoint.
- `GET /api/me` returns the authenticated public identity.

Copy `.env.example` to `.env` and set local values for `JWT_SECRET_KEY`, `SEED_SUPERADMIN_EMAIL`, and `SEED_SUPERADMIN_PASSWORD`. Then apply migrations and run the idempotent seed command:

```sh
docker compose exec backend flask db upgrade
docker compose exec backend flask seed
```

The frontend stores the short-lived access token under `cms_access_token`, restores it through `/api/me`, attaches it as a bearer token, and clears it on logout or an invalid session. The `/system-access` route is intentionally unlinked from navigation and calls only the Superadmin endpoint.

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

- `backend/`: Flask application factory, extensions, domain models, authentication Blueprints, seed command, and pytest suite
- `frontend/`: Vite/React application, router, persistent auth context, shared API client, login screens, and Vitest suite
- `migrations/`: tracked Flask-Migrate/Alembic environment
- `compose.yaml`: canonical development runtime and persistent volumes

## Optional host-native troubleshooting

Compose remains the supported workflow. If diagnosing a container-specific issue, equivalent host-native commands are `flask --app backend.app:create_app run --debug` after installing `backend/requirements.txt`, and `npm run dev` from `frontend/` after `npm ci`. A host-native backend needs a host-reachable `DATABASE_URL`, such as `postgresql+psycopg://cms:cms@localhost:5432/cms`.
