# CMS

This repository contains a Dockerized role-based CMS built with Flask, React, and PostgreSQL. Docker Compose is the canonical runtime: it starts PostgreSQL 18, the Flask API, and the Vite/React frontend together with health checks and source reload.

Milestones 1–5 are complete: the repository includes the runnable application skeleton, migrated domain schema, JWT authentication, numeric role enforcement, frontend session restoration, content CRUD, taxonomy management, guarded user administration, a secure media library, and the public reading experience. The reusable frontend foundation supplies the shared route shells, navigation, controls, homepage composition, and co-located stylesheet modules. Milestone 6 then delivers the complete dashboard and publisher pictures. Site-wide settings remain later work.

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

Open <http://localhost:5173>. The home page loads published announcements, articles, categories, and featured images from the Flask API. PostgreSQL is exposed on `localhost:5432` with the configured `POSTGRES_*` values.

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

Only use `docker compose down --volumes` when you intentionally want to erase local PostgreSQL data, uploaded media, and the container-managed frontend dependencies.

Rebuild after changing dependencies or Dockerfiles:

```sh
docker compose build --no-cache backend frontend
docker compose up -d
```

The frontend development command is `vite --host 0.0.0.0` (`npm run dev`). After changing that script, restart it with `docker compose restart frontend`. Production bundles use the separate build command below.

For a blank screen, capture the failed module request in the affected browser’s Network panel: URL, status, response, redirects, and blocking reason, together with the console startup error. A successful server response or a clean browser check alone does not establish that the affected profile works. See [the stabilization acceptance record](docs/reports/frontend-stabilization.md).

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

Tokens record whether they came from regular or Superadmin login. If an Admin is promoted to Superadmin, their existing regular token is rejected and they must authenticate through `/system-access`; authorization always uses the current database role.

## Content API

The content API uses JSON request and response bodies. Collection responses use `{"items": [...]}` and individual resources use `{"item": {...}}`.

- `GET /api/articles` and `GET /api/articles/slug/<slug>` expose published articles publicly.
- `GET /api/announcements` exposes current published announcements publicly and omits expired announcements.
- `GET /api/pages` and `GET /api/pages/slug/<slug>` expose published pages publicly.
- Authenticated management uses the collection endpoints plus `GET`, `PUT`, and `DELETE` at `/<id>`.

Publishers can create and manage only their own draft articles and announcements, and can submit them with `status: "pending_review"`. Submitted content becomes read-only to its Publisher until an Admin acts on it. Admins and Superadmins can manage any content, publish it with `status: "published"`, or return it to draft. Only Admins and Superadmins can create or manage pages.

Article requests require an existing `category_id`. Optional `tag_ids` values must reference existing tags. A `featured_image_id` must reference an uploaded image; article responses retain that ID and include a nested `featured_image` object when present.

## Public frontend

The public React routes are available without login:

- `/` shows current announcements and published articles in an editorial layout.
- `/articles/<slug>` shows a published article and its uploaded featured image.
- `/announcements` shows all current published announcements.
- `/pages/<slug>` shows a published static page.

Public content requests deliberately omit any stored bearer token, so an expired browser session cannot hide otherwise public material. Article and page bodies render as plain text with paragraph breaks preserved; stored HTML is never injected into the document. Markdown and rich provider embeds remain later extensions.

The homepage loads articles, announcements, and category metadata independently. If category metadata is unavailable, articles remain readable without labels; if one content section fails, the other successful sections remain visible and the failed section provides a retry action.

## Administration API

Category and tag collections are public so published content can resolve its taxonomy. Mutation requires Admin or Superadmin access:

- `GET/POST /api/categories` and `GET/PUT/DELETE /api/categories/<id>`
- `GET/POST /api/tags` and `GET/PUT/DELETE /api/tags/<id>`

Media management requires Admin or Superadmin access:

- `GET /api/media` and `GET/PUT/DELETE /api/media/<id>`
- `POST /api/media/uploads` accepts a multipart `file` plus optional `alt_text`.
- `POST /api/media/links` accepts an HTTPS `url` plus optional `alt_text`.
- `GET /api/media/files/<storage-key>` publicly serves an uploaded image.

Uploads accept JPEG, PNG, WebP, and non-animated GIF images. They are limited by `MEDIA_MAX_BYTES` and `MEDIA_MAX_PIXELS`, decoded and re-encoded, stripped of metadata, and stored under generated names in the persistent `media_uploads` volume. SVG is not accepted. External links are normalized and classified as YouTube, Facebook, Instagram, or generic without fetching the remote URL or accepting embed HTML.

User management uses `GET/POST /api/users` and `GET/PUT/DELETE /api/users/<id>`. Admins can manage Publisher accounts only. Superadmins can manage every role, but cannot delete or demote their active account. Referenced taxonomy, media, and users return `409` until content is explicitly reassigned or detached.

## Database migrations

The tracked Alembic history contains the initial CMS domain schema, the announcement-review status revision, and the source-aware media asset revision.

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

- `backend/`: Flask application factory, feature Blueprints, domain models, authentication/authorization helpers, media storage adapter, seed command, and pytest suite
- `frontend/`: Vite/React application, public reading experience, router, persistent auth context, shared API client, login screens, and Vitest suite
- `migrations/`: tracked Flask-Migrate/Alembic environment
- `compose.yaml`: canonical development runtime with persistent PostgreSQL, uploaded-media, and frontend-dependency volumes

## Frontend composition and themes

The reusable frontend foundation separates route-area shells from shared site chrome and page content:

- `frontend/src/layouts/PublicLayout.jsx`, `AuthLayout.jsx`, and `DashboardLayout.jsx` own the outer structure for public, authentication, and dashboard routes.
- `frontend/src/components/layout/Header.jsx`, `Navigation.jsx`, and `Footer.jsx` own reusable site chrome. Edit these files for global header, navigation, and footer changes.
- `frontend/src/components/ui/Button.jsx` and `FormField.jsx` are shared controls. Page-specific controls should compose or extend these patterns without duplicating their behavior and states.
- `frontend/src/components/home/HomeIntro.jsx`, `AnnouncementSection.jsx`, and `ArticleSection.jsx` present the homepage. `frontend/src/hooks/useHomeContent.js` loads the homepage data, and `frontend/src/pages/public/Home.jsx` is the edit point for the section order.
- `frontend/src/styles.css` is the single source of global reset and theme tokens. Layout, page, and component rules belong in co-located CSS Modules and consume those tokens.

Milestone 6 depends on this foundation. It keeps the planned role-aware dashboard, editorial workflow, and Publisher-owned picture upload and rendering requirements. Superadmin site-wide settings are a later milestone.

## Optional host-native troubleshooting

Compose remains the supported workflow. If diagnosing a container-specific issue, equivalent host-native commands are `flask --app backend.app:create_app run --debug` after installing `backend/requirements.txt`, and `npm run dev` from `frontend/` after `npm ci`. A host-native backend needs a host-reachable `DATABASE_URL`, such as `postgresql+psycopg://cms:cms@localhost:5432/cms`.
