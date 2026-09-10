# CMS

This repository contains a Dockerized role-based CMS built with Flask, React, and PostgreSQL. Docker Compose is the canonical runtime: it starts PostgreSQL 18, the Flask API, and the Vite/React frontend together with health checks and source reload.

Milestones 1 and 2 are complete: the repository includes the runnable application skeleton, domain schema and Alembic migration, backend authentication, JWT sessions, numeric role enforcement, Superadmin isolation, rate limits, and frontend login/session restoration.

Milestone 3 adds backend authorization and CRUD for articles, announcements, and pages, including Publisher ownership boundaries and published-only public responses. Taxonomy and user management, media uploads, public content screens, and the complete dashboard remain later work.

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

## Content API

The content API uses JSON request and response bodies. Collection responses use `{"items": [...]}` and individual resources use `{"item": {...}}`.

- `GET /api/articles` and `GET /api/articles/slug/<slug>` expose published articles publicly.
- `GET /api/announcements` exposes current published announcements publicly and omits expired announcements.
- `GET /api/pages` and `GET /api/pages/slug/<slug>` expose published pages publicly.
- Authenticated management uses the collection endpoints plus `GET`, `PUT`, and `DELETE` at `/<id>`.

Publishers can create and manage only their own draft articles and announcements, and can submit them with `status: "pending_review"`. Submitted content becomes read-only to its Publisher until an Admin acts on it. Admins and Superadmins can manage any content, publish it with `status: "published"`, or return it to draft. Only Admins and Superadmins can create or manage pages.

Article requests require an existing `category_id`. Optional `tag_ids` and `featured_image_id` values must reference existing records. Category, tag, and media management endpoints are planned for later milestones; the seed command supplies initial categories.

## Database migrations

The tracked Alembic history contains the initial CMS domain schema and the Milestone 3 announcement-review status revision.

Apply revisions and inspect migration state:

```sh
docker compose exec backend flask db upgrade
docker compose exec backend flask db current
docker compose exec backend flask db heads
```

When a model change requires a schema revision, create it with:

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
