# Build Prompt: Role-Based CMS (React + Flask + PostgreSQL)

## Project Overview
Build a full-stack Content Management System with a React frontend and a Python (Flask) backend, connected via a REST API, using PostgreSQL as the database.

The site has a public-facing homepage showing announcements and news articles, plus an authenticated dashboard for content management with role-based access control.

This document describes the complete CMS target. Delivery is incremental: a milestone may intentionally contain placeholders for requirements assigned to a later milestone. Unless a requirement is explicitly included in a milestone, it remains part of the final deliverable rather than the acceptance scope for that milestone.

---

## Milestone 1: Runnable Project Skeleton

Milestone 1 establishes a locally runnable Flask/React project and its integration boundaries. It must make later feature work straightforward, but it does not implement the CMS domain yet.

### Scope

- Create a Flask backend using an application factory and feature-oriented Blueprint placeholders matching the final backend structure.
- Create a React frontend with Vite, React Router, the final top-level page/component/service folders, and placeholder pages for the public, login, and dashboard routes.
- Make Docker Compose the required Milestone 1 runtime. `docker compose up --build` must start PostgreSQL, Flask, and Vite together; Flask runs at `http://localhost:5000`, Vite at `http://localhost:5173`, and PostgreSQL at `localhost:5432`.
- Add `GET /api/health`, returning JSON such as `{"status": "ok"}` with HTTP `200`.
- Configure CORS for the frontend origin and add a small frontend API client. The visible home placeholder must call the health endpoint and show a clear connected or unavailable state, proving the browser can reach Flask.
- Add importable placeholder backend modules for auth, articles, announcements, pages, media, categories, tags, and users. Add the corresponding frontend route, page, context, and service modules needed by the final structure. Placeholders need not expose feature CRUD endpoints.
- Wire SQLAlchemy and Flask-Migrate into the Flask application factory and configuration. Initialize and track the Alembic migration environment so future model migrations can be generated consistently.
- Provide `.env.example`, root `.gitignore`, and a root `README.md` with exact Compose startup, shutdown, logs, rebuild, test, frontend build, PostgreSQL, environment, and migration commands. Host-native commands may appear only as optional troubleshooting guidance.
- Add service Dockerfiles, health checks, source bind mounts, a container-managed frontend `node_modules` volume, and a persistent PostgreSQL data volume.

### Placeholder behavior

- `/login` and the unlinked `/system-access` route render an explicit "Login is not available in Milestone 1" state. They must not imply that authentication works or store a fake token.
- Every `/dashboard` route redirects to `/login` while authentication is unavailable. This temporary behavior is replaced by role-aware protected routes in a later milestone.
- Any unimplemented backend route below `/api/` returns a JSON `404` response, for example `{"error": "Not found"}`. It must not return Flask's default HTML error page.
- Public content pages may render labeled placeholders until their APIs and models are implemented.

### Deferred from Milestone 1

The following requirements remain mandatory for the full CMS, but are deferred to later milestones:

- domain models, relationships, indexes, and the application schema;
- schema-generating migrations for those models and any production data migration;
- signup, login, JWT handling, password hashing, ownership checks, and role authorization;
- working content, taxonomy, media, and user-management CRUD;
- file upload and storage behavior;
- a working seed command and seed data.

Migration tooling is in scope for Milestone 1; domain migration content is not. Alembic configuration and migration files must be committed to version control rather than generated only on a developer's machine. When migrations are later added, the project must verify that `flask db upgrade` works against the supported PostgreSQL version and that the resulting schema is compatible with the configured SQLAlchemy and database-driver versions.

### Stack decisions and comparison

| Concern | Selected for this project | Alternatives considered | Reason for the skeleton choice |
|---|---|---|---|
| Backend web framework | Flask with Blueprints and an application factory | Django, FastAPI | Matches the full specification while keeping the first milestone small and modular. |
| Frontend build tool | React with Vite | Create React App, a server-rendered framework | Provides a fast development server and a minimal client-only scaffold; Create React App is no longer the preferred new-project baseline. |
| Database access | SQLAlchemy + Flask-Migrate/Alembic | Raw SQL, `db.create_all()` | Preserves an explicit migration history and supports the relational domain planned for later milestones. |
| PostgreSQL driver | `psycopg` | `psycopg2` | Current driver line with PostgreSQL support; pin a compatible version in backend dependencies. |
| HTTP client | A small wrapper around browser `fetch` | Axios | The skeleton needs only base-URL handling and JSON/error normalization, so an extra runtime dependency is unnecessary. |
| Local runtime | Three-service Docker Compose stack with PostgreSQL, Flask, and Vite | Independent host-native processes; serving a built frontend from Flask | Gives Milestone 1 a reproducible one-command runtime while preserving source reload and clear service boundaries. |

### Configuration defaults

Configuration must come from environment variables, with safe local defaults where indicated:

| Variable | Milestone 1 default/example | Purpose |
|---|---|---|
| `FLASK_APP` | `backend.app:create_app` | Flask application factory entry point |
| `FLASK_DEBUG` | `1` for local development | Enables the local debugger and reload behavior |
| `SECRET_KEY` | required placeholder in `.env.example` | Flask signing secret; no real value is committed |
| `POSTGRES_DB` | `cms` | PostgreSQL database created by Compose |
| `POSTGRES_USER` | `cms` | PostgreSQL user created by Compose |
| `POSTGRES_PASSWORD` | `cms` | Local-only PostgreSQL password example |
| `DATABASE_URL` | `postgresql+psycopg://cms:cms@db:5432/cms` | Compose PostgreSQL connection used by SQLAlchemy and migrations |
| `FRONTEND_ORIGIN` | `http://localhost:5173` | Exact origin allowed by backend CORS configuration |
| `VITE_API_BASE_URL` | `http://localhost:5000/api` | Frontend API base URL |

The backend must load a root or backend `.env` file consistently with the README. Environment-specific secrets stay untracked. Vite exposes only variables prefixed with `VITE_`, so secrets must never use that prefix.

### Acceptance checks

Milestone 1 is complete only when all of the following have been verified from a clean checkout:

1. `docker compose config`, `docker compose build`, and `docker compose up -d` succeed, and all three service health checks pass.
2. `GET http://localhost:5000/api/health` returns HTTP `200` with exact JSON `{"status":"ok"}`, and the Vite homepage reports a successful backend health connection.
3. A request to an unknown `/api/...` path returns JSON with HTTP `404`; a non-API unknown path may use the normal Flask response.
4. `/login` and `/system-access` state that login is unavailable, and direct navigation to `/dashboard` or a nested dashboard URL redirects to `/login`.
5. Backend placeholder modules import successfully and the frontend production build completes without unresolved imports.
6. Flask-Migrate commands load the application, the tracked Alembic environment is present, and migration status/history can be inspected. Milestone 1 must not fabricate domain tables merely to make a migration non-empty.
7. The README Compose commands work with the documented defaults, the PostgreSQL volume persists across a normal stop/start, `.env` files and generated artifacts remain ignored, and migration files remain tracked.
8. Dependency versions selected for Flask, SQLAlchemy, Flask-Migrate, Alembic, `psycopg`, React, Vite, and React Router are mutually compatible at runtime; verification must include starting both applications, not only successful installation.

---

## 1. Roles (inherited hierarchy — each role has all permissions of the role below it, plus more)

| Role | Permissions |
|---|---|
| **Visitor** (unauthenticated) | View published articles, announcements, and pages only |
| **Publisher** | + Create, edit, and delete their OWN articles and announcements (as drafts); submit drafts for review |
| **Admin** | + Publish/unpublish any content; edit/delete any user's content; manage categories and tags; manage media library; create/manage Publisher accounts |
| **Superadmin** | + Manage Admin accounts; full user management (create/edit/delete any user, any role); manage site-wide settings; delete any content unconditionally |

Implement role-checking as a reusable decorator/middleware pattern (e.g., `@role_required("admin")`) using numeric role levels for comparison, not string matching.

---

## 2. Content Types & Data Models

Design and implement database models for:

- **User** — id, email, password_hash, role (enum: visitor/publisher/admin/superadmin), created_at
- **Article** — id, title, slug, body, status (draft/pending_review/published), author_id (FK to User), category_id (FK), featured_image_id (FK to Media), created_at, updated_at, published_at
- **Announcement** — id, title, body, status (draft/published), author_id (FK to User), created_at, published_at, expires_at (optional)
- **Page** — id, title, slug, body, status (draft/published), author_id (FK to User), updated_at (for static pages like About/Contact)
- **Category** — id, name, slug
- **Tag** — id, name, slug (many-to-many with Article)
- **Media** — id, filename, url, uploaded_by (FK to User), uploaded_at, file_type, source_type, media_type, provider, storage_key, alt_text. Milestone 4 supports locally stored images and external HTTPS links through the same source-aware record. Provider metadata is descriptive only: the backend does not fetch arbitrary URLs or store raw embed HTML.

Use an ORM (SQLAlchemy) to define these models and their relationships. Include foreign key constraints and appropriate indexes on slug fields.

---

## 3. Backend Requirements (Flask)

**Structure:**
```
backend/
├── routes/
│   ├── auth.py
│   ├── articles.py
│   ├── announcements.py
│   ├── pages.py
│   ├── media.py
│   ├── categories.py
│   ├── tags.py
│   └── users.py
├── models/
│   ├── user.py
│   ├── article.py
│   ├── announcement.py
│   ├── page.py
│   ├── category.py
│   ├── tag.py
│   └── media.py
├── utils/
│   └── auth_helpers.py
├── app.py
├── config.py
├── requirements.txt
└── .env.example
```

**Auth:**
- `/api/signup` — create account (default role: visitor; publisher+ accounts created via admin panel, not public signup)
- `/api/login` — email + password for Visitor, Publisher, and Admin roles, returns a JWT
- `/api/superadmin-login` — SEPARATE endpoint, only for Superadmin accounts. Must reject login attempts from any non-superadmin user even with correct credentials (checked after password verification). Recommended: rate-limit this endpoint more strictly than `/api/login`, and log all attempts (success and failure) with timestamp + IP.
- Passwords hashed with `werkzeug.security` (never store plain text)
- JWT includes user id and role; verify and decode on every protected request
- `login_required` decorator for any authenticated route
- `role_required(min_role)` decorator for role-gated routes

**API endpoints needed (REST conventions, JSON in/out):**
- Full CRUD for Articles, Announcements, Pages, Categories, Tags, Media
- `GET` endpoints for public content should only return `status=published` items when no valid auth token is present
- `POST/PUT/DELETE` endpoints must check both authentication AND role/ownership (a Publisher can only edit their own drafts; Admin+ can edit anyone's)
- Media upload endpoint that accepts file uploads and stores them (local disk storage is fine for now; return a URL)
- External media-link creation for HTTPS URLs, with known-provider classification and no server-side preview fetch. Rich oEmbed/provider adapters, additional upload types, and Markdown rendering remain later extensions of this boundary.
- User management endpoints (`/api/users`) restricted to Admin (view/manage Publishers) and Superadmin (view/manage everyone including Admins)

**Other requirements:**
- Use Flask Blueprints to organize routes by feature
- Use `flask-cors` to allow the frontend origin
- Use environment variables (via `.env` + `python-dotenv`) for `SECRET_KEY`, database URL, etc. — provide a `.env.example` with placeholder values
- Include a `config.py` that loads these settings
- Include basic input validation and proper HTTP status codes (200, 201, 400, 401, 403, 404)
- Use **Flask-Migrate** (Alembic under the hood) for database migrations. Initialize it during project setup and commit the generated migration environment and subsequent revision files. The README must explain that `flask db init` is a one-time maintainer command, document `flask db migrate` for creating reviewed revisions, and use `flask db upgrade` in normal fresh-checkout setup. Do not rely on `db.create_all()` alone for schema management.

---

## 4. Frontend Requirements (React)

**Structure:**
```
frontend/
├── src/
│   ├── components/
│   │   ├── layout/       (Header, Navigation, Footer)
│   │   ├── content/       (ArticleCard, AnnouncementCard, MediaUploader)
│   │   ├── home/          (HomeIntro, AnnouncementSection, ArticleSection)
│   │   └── ui/            (Button, FormField, LoadingSpinner, generic reusable pieces)
│   ├── layouts/           (PublicLayout, AuthLayout, DashboardLayout)
│   ├── pages/
│   │   ├── public/        (Home, ArticlePage, AnnouncementsPage, PageView)
│   │   ├── auth/           (Login, SuperadminLogin)
│   │   └── dashboard/     (DashboardHome, ArticleEditor, AnnouncementEditor,
│   │                        ManageUsers, ManageCategories, MediaLibrary)
│   ├── context/
│   │   └── AuthContext.jsx
│   ├── hooks/
│   │   └── useHomeContent.js
│   ├── services/
│   │   ├── api.js          (base fetch wrapper, includes auth token automatically)
│   │   ├── articles.js
│   │   ├── announcements.js
│   │   └── auth.js
│   ├── routes/
│   │   └── ProtectedRoute.jsx   (role-gated route wrapper)
│   ├── styles.css        (global reset and theme-token source)
│   ├── App.jsx
│   └── main.jsx
└── package.json
```

**Homepage (`pages/public/Home.jsx`):**
- Fetches and displays a list of published Announcements (e.g., a banner or top section)
- Fetches and displays a list of published Articles in a newspaper-style layout (headline + summary cards)
- No login required to view

**Reusable frontend foundation:**
- Establish the reusable frontend foundation before adding dashboard screens. It provides the public, authentication, and dashboard shells and remains the shared presentation boundary for subsequent frontend milestones.
- Route-area shells live in `src/layouts/PublicLayout.jsx`, `AuthLayout.jsx`, and `DashboardLayout.jsx`. They own the appropriate outer structure and navigation placement; pages compose their content inside the relevant shell rather than duplicating chrome.
- Shared site chrome lives in `src/components/layout/Header.jsx`, `Navigation.jsx`, and `Footer.jsx`. Update these components to change global header, navigation, or footer behavior and content.
- Shared controls live in `src/components/ui/`, beginning with `Button.jsx` and `FormField.jsx`. Reuse these controls for consistent interactive and accessible states; keep page-specific presentation out of the generic controls.
- Homepage presentations live in `src/components/home/`: `HomeIntro.jsx`, `AnnouncementSection.jsx`, and `ArticleSection.jsx`. `src/hooks/useHomeContent.js` owns the homepage's coordinated data loading. `Home.jsx` composes those sections and is the single edit point for their display order.
- `src/styles.css` is the source of truth for global reset and theme tokens. Layout, page, and component rules move into co-located CSS Modules and consume those tokens; they must not introduce competing global theme values.
- The foundation must preserve React Router, the shared API-client architecture, role-aware protected routes, and the existing public-content behavior while making each layout and component focused on one responsibility.

**Auth:**
- `AuthContext` stores JWT (in memory + localStorage) and current user's role
- `services/api.js` automatically attaches the token to requests when present
- `ProtectedRoute` component wraps dashboard routes and checks the user's role against a required minimum, redirecting unauthorized users

**Dashboard (authenticated, role-aware):**
- Publisher: sees only their own content in editable lists, with a "New Article" / "New Announcement" button
- Admin: additionally sees ALL users' content, a "Publish/Unpublish" toggle, category/tag management, media library
- Superadmin: additionally sees user management (create/edit/delete Admins and Publishers, change roles)
- Use conditional rendering based on role to show/hide dashboard sections and buttons — don't rely on hiding alone for security, the backend must also enforce it

**Site-wide settings (later milestone):**
- Superadmins must be able to manage site-wide settings through backend-authorized APIs and a corresponding dashboard experience. The settings model, persistence, validation, audit/authorization behavior, and public application of settings remain outstanding after the reusable frontend foundation and Milestone 6.

**Routing:**
- Use React Router
- Public routes: `/`, `/articles/:slug`, `/announcements`, `/pages/:slug`, `/login`
- Superadmin login: a separate, unlinked route (e.g., `/system-access` or similar non-obvious path — not linked from any nav/UI, must be typed/bookmarked directly). This page calls `/api/superadmin-login` instead of `/api/login`, and should look visually distinct from the regular login page so it's clear which account type it's for
- Dashboard routes: `/dashboard`, `/dashboard/articles/new`, `/dashboard/articles/:id/edit`, `/dashboard/users` (admin+), etc.
- After a successful superadmin login, redirect into the same `/dashboard`, since permissions are still enforced by role on every route and API call — the separate login page is about isolating the entry point, not creating a separate app

---

## 5. Non-Functional Requirements

- Include a root `README.md` explaining: project structure, how to run backend (`pip install -r requirements.txt`, set up `.env`, run migrations, `flask run`), how to run frontend (`npm install`, `npm run dev`), and how the two connect
- Include a `.gitignore` for both frontend and backend (node_modules, __pycache__, .env, venv, build artifacts)
- Backend should include a simple database seed script that creates one Superadmin account and a few sample categories, so the app is usable immediately after setup. The Superadmin's initial email and password must be read from environment variables (e.g., `SEED_SUPERADMIN_EMAIL`, `SEED_SUPERADMIN_PASSWORD` in `.env.example` with placeholder values) — never hardcode real or example credentials directly in the seed script
- Keep components and route handlers small and single-purpose — one file, one responsibility
- Add brief comments explaining non-obvious logic, especially around role-checking and JWT handling

---

## 6. Final Deliverable

The final deliverable is the complete CMS described in Sections 1–5: a working Flask backend with all models, routes, authentication, and role logic; a working React frontend with public and dashboard experiences, auth context, and protected routes; and a README with setup instructions. The completed code must run locally with a PostgreSQL database after following the README steps.

Milestone 1 is the first incremental delivery toward that target and is accepted only against the scope and checks in “Milestone 1: Runnable Project Skeleton.” Its explicit placeholders and deferrals do not remove or weaken any final-deliverable requirement. Later milestones must replace the placeholder login, dashboard redirects, public content, and API behavior with the corresponding complete functionality in Sections 1–5.
