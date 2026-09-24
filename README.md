# CMS

**A self-hosted, role-based content platform for teams who publish — without handing editors the keys to the server.**

Think of it as the editorial backbone behind a news site, company blog, or membership portal: writers draft, editors approve, admins govern, and the public gets a clean reading experience — all backed by a Flask API, a React front end, and PostgreSQL, running anywhere Docker runs.

## Why teams use it

- **Clear roles, no gray areas.** Publishers write and submit; Admins review, publish, or send work back; Superadmins govern the whole system through a separate, unlisted access point. Everyone sees exactly what their role allows — nothing more.
- **An editorial workflow, not just a database table.** Drafts move through submission and review before they ever go live, so nothing gets published by accident.
- **Built-in media handling.** Writers upload images directly; the system re-encodes them, strips hidden metadata, and only exposes a file publicly once it's actually referenced by published content.
- **A fast, distraction-free public site.** Articles, announcements, and pages render instantly for visitors, with independent sections that keep degrading gracefully — one broken feed never takes down the rest of the homepage.
- **Runs anywhere Docker does.** One command boots the database, API, and front end together, with health checks and hot reload for active development.

## What's inside

| Layer | Tech | Role |
|---|---|---|
| Frontend | React + Vite | Public site and role-aware dashboards |
| Backend | Flask | REST API, auth, and business rules |
| Database | PostgreSQL 18 | Content, taxonomy, users, and media metadata |
| Runtime | Docker Compose | One-command local and staging environments |

The mandatory CMS milestones cover the runnable application, migrated domain schema, authentication, content APIs, public reading experience, publisher editing, and Admin administration screens. Site settings are persistent and editable by Superadmins. Chromium and Firefox browser acceptance passed; results are recorded in `TODO.md` and the stabilization report.

---

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

For a blank screen, capture the failed module request in the affected browser’s Network panel: URL, status, response, redirects, and blocking reason, together with the console startup error. A successful server response or a clean browser check alone does not establish that the affected profile works. See [the stabilization acceptance record](docs/reports/milestone-6/05-frontend-stabilization-acceptance.md).

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

Run the browser acceptance suite in its disposable Compose setup. It creates
test-only Publisher, Admin, and Superadmin accounts, then verifies public
startup, both sign-in flows, publishing, image visibility, unpublishing, and a
published page route, administration screens, role boundaries, and site settings
in Chromium and Firefox:

```sh
docker compose -p cms-e2e -f compose.yaml -f compose.e2e.yaml run --build --rm e2e
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

Authenticated dashboard routes cover article and announcement lists/editors for Publishers, plus page management for Admins and Superadmins: `/dashboard/articles`, `/dashboard/announcements`, and `/dashboard/pages`. Editors support ordered text and picture blocks, status workflows, private picture previews, and expiry dates for announcements.

Admins and Superadmins can open `/dashboard/categories`, `/dashboard/tags`, `/dashboard/media`, and `/dashboard/users`. These screens support create, edit, delete, loading, retry, and API errors. The media screen accepts local image uploads and HTTPS links. Admin user management is limited to Publisher accounts. Superadmins can manage all permitted roles and open `/dashboard/settings`.

The content API uses JSON request and response bodies. Collection responses use `{"items": [...]}` and individual resources use `{"item": {...}}`.

- `GET /api/articles` and `GET /api/articles/slug/<slug>` expose published articles publicly.
- `GET /api/announcements` exposes current published announcements publicly and omits expired announcements.
- `GET /api/pages` and `GET /api/pages/slug/<slug>` expose published pages publicly.
- Authenticated management uses the collection endpoints plus `GET`, `PUT`, and `DELETE` at `/<id>`.

Publishers can create and manage only their own draft articles and announcements, and can submit them with `status: "pending_review"`. Submitted content becomes read-only to its Publisher until an Admin acts on it. Admins and Superadmins can manage any content, publish it with `status: "published"`, or return it to draft. Only Admins and Superadmins can create or manage pages.

Article requests require an existing `category_id`. Optional `tag_ids` values must reference existing tags. A `featured_image_id` must reference an uploaded image; article responses retain that ID and include a nested `featured_image` object when present.

Content requests may send either a plain-text `body` or an ordered `body_blocks` array. Text blocks use `{"type":"text","text":"..."}` and image blocks use `{"type":"image","media_id":123}`. Responses include both the plain-text `body` projection and `body_blocks`; image blocks include resolved media metadata. Sending both fields is rejected, while a body-only write remains compatible and becomes one text block.

## Public frontend

The article dashboard preserves existing text/picture blocks and publication status on ordinary saves. Draft authors can upload or reuse permitted pictures, add and reorder text sections, detach pictures, and preview private uploads without placing credentials in image URLs. Publishers edit drafts and submit saved drafts for review, while Admins and Superadmins can publish, unpublish, or return submitted work to draft. Announcement and page dashboards provide the same ordered-block editing and status workflows, with announcement expiry and Admin-gated page management.

The public React routes are available without login:

- `/` shows current announcements and published articles in an editorial layout.
- `/articles/<slug>` shows a published article, its uploaded featured image, and ordered inline picture blocks.
- `/announcements` shows all current published announcements.
- `/pages/<slug>` shows a published static page.

Public content requests deliberately omit any stored bearer token, so an expired browser session cannot hide otherwise public material. Article and page bodies render as plain text with paragraph breaks preserved; stored HTML is never injected into the document. Markdown and rich provider embeds remain later extensions.

The homepage loads articles, announcements, and category metadata independently. If category metadata is unavailable, articles remain readable without labels; if one content section fails, the other successful sections remain visible and the failed section provides a retry action.

## Administration API

Category and tag collections are public so published content can resolve its taxonomy. Mutation requires Admin or Superadmin access:

- `GET/POST /api/categories` and `GET/PUT/DELETE /api/categories/<id>`
- `GET/POST /api/tags` and `GET/PUT/DELETE /api/tags/<id>`

Publishers may upload and list only their own images. Admins and Superadmins can list all media and retain global editing, deletion, and external-link creation:

- `GET /api/media` and `GET/PUT/DELETE /api/media/<id>`
- `POST /api/media/uploads` accepts a multipart `file` plus optional `alt_text`.
- `POST /api/media/links` accepts an HTTPS `url` plus optional `alt_text`.
- `GET /api/media/files/<storage-key>` serves an uploaded image to its owner or an Admin; it becomes public only while referenced by published content and is rechecked after unpublishing.

Uploads accept JPEG, PNG, WebP, and non-animated GIF images. They are limited by `MEDIA_MAX_BYTES` and `MEDIA_MAX_PIXELS`, decoded and re-encoded, stripped of metadata, and stored under generated names in the persistent `media_uploads` volume. SVG is not accepted. External links are normalized and classified as YouTube, Facebook, Instagram, or generic without fetching the remote URL or accepting embed HTML.

User management uses `GET/POST /api/users` and `GET/PUT/DELETE /api/users/<id>`. Admins can manage Publisher accounts only. Superadmins can manage every role, but cannot delete or demote their active account. Referenced taxonomy, media, and users return `409` until content is explicitly reassigned or detached.

`GET /api/settings` returns public site name, tagline, homepage headline, and homepage intro text. `PUT /api/settings` requires a Superadmin token. It accepts those four text fields, trims whitespace, rejects empty or overlong values, and writes an append-only before/after change record with actor and time. The public response contains no change log data. Saved copy appears in the header, footer, and homepage. Apply `flask db upgrade` before using this endpoint on an existing database.

## Database migrations

The tracked Alembic history contains the initial CMS domain schema, the announcement-review status revision, the source-aware media asset revision, the ordered content-block backfill revision, and persistent site settings with change history.

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

- `docs/`: [documentation index](docs/README.md) and milestone reports
- `backend/`: Flask application factory, feature Blueprints, domain models, authentication/authorization helpers, media storage adapter, seed command, and pytest suite
- `frontend/`: Vite/React application, public reading experience, article-authoring dashboard routes, router, persistent auth context, shared API client, login screens, and Vitest suite
- `migrations/`: tracked Flask-Migrate/Alembic environment
- `compose.yaml`: canonical development runtime with persistent PostgreSQL, uploaded-media, and frontend-dependency volumes

## Frontend composition and themes

The reusable frontend foundation separates route-area shells from shared site chrome and page content:

- `frontend/src/layouts/PublicLayout.jsx`, `AuthLayout.jsx`, and `DashboardLayout.jsx` own the outer structure for public, authentication, and dashboard routes.
- `frontend/src/components/layout/Header.jsx`, `Navigation.jsx`, and `Footer.jsx` own reusable site chrome. Edit these files for global header, navigation, and footer changes.
- `frontend/src/components/ui/Button.jsx` and `FormField.jsx` are shared controls. Page-specific controls should compose or extend these patterns without duplicating their behavior and states.
- `frontend/src/components/home/HomeIntro.jsx`, `AnnouncementSection.jsx`, and `ArticleSection.jsx` present the homepage. `frontend/src/hooks/useHomeContent.js` loads the homepage data, and `frontend/src/pages/public/Home.jsx` is the edit point for the section order.
- `frontend/src/styles.css` is the single source of global reset and theme tokens. Layout, page, and component rules belong in co-located CSS Modules and consume those tokens.

Markdown rendering, rich provider embeds, and non-image uploads remain future extensions.

## Optional host-native troubleshooting

Compose remains the supported workflow. If diagnosing a container-specific issue, equivalent host-native commands are `flask --app backend.app:create_app run --debug` after installing `backend/requirements.txt`, and `npm run dev` from `frontend/` after `npm ci`. A host-native backend needs a host-reachable `DATABASE_URL`, such as `postgresql+psycopg://cms:cms@localhost:5432/cms`.
