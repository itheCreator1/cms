# Architecture Audit Report — CMS (Flask + React + PostgreSQL)

**Date:** 2026-09-09
**Scope:** Expandability, Modularity, Maintainability
**Version:** Milestone 2 (post-auth foundation)

---

## Executive Summary

| Dimension       | Score   | Verdict                                                        |
|-----------------|---------|----------------------------------------------------------------|
| Expandability   | 3.0/5   | Solid base, but no abstractions for repeated patterns          |
| Modularity      | 4.0/5   | Strong separation of concerns, clean model layer               |
| Maintainability | 4.3/5   | Excellent readability, tests, and error handling                |
| **Overall**     | **3.8/5** | Well-structured early-stage project with clear discipline, but lacks the abstractions needed to scale efficiently |

---

## 1. Expandability — 3.0/5

### 1.1 Adding a New Content Type (e.g. "Event") — 3/5

| File | Action |
|------|--------|
| `backend/models/events.py` | Create SQLAlchemy model (new) |
| `backend/models/__init__.py` | Import and add to `__all__` |
| `backend/models/users.py` | Add relationship on User model |
| `backend/routes/events.py` | Create Blueprint stub (new) |
| `backend/routes/__init__.py` | Import and add to `blueprints` tuple |
| Alembic migration | `flask db migrate` |
| `frontend/src/services/events.js` | Create service module (new) |
| `frontend/src/App.jsx` | Add new `<Route>` entries |
| Frontend pages | Create page components (new) |

**6–10 files** must be touched per new content type.

- ✅ Blueprint pattern is consistent and clean
- ✅ Models follow uniform conventions (title, slug, body, status, author FK, timestamps)
- ❌ No `PublishableMixin` or abstract base — shared columns are copy-paste
- ❌ User model must be modified for every new author-linked content type
- ❌ Frontend routes are flat in `App.jsx` — no dynamic registration

### 1.2 Adding a New Role — 2/5

- ✅ Numeric level system in `utils/auth_helpers.py:10-15` is conceptually sound
- ✅ `role_required` decorator compares levels naturally
- ❌ `UserRole` is a PostgreSQL ENUM — adding values requires a migration (`ALTER TYPE ... ADD VALUE`), additive-only
- ❌ `ROLE_LEVELS` is a plain dict in a separate file from the enum — no compiler enforcement of sync
- ❌ Hardcoded role sets in `routes/auth.py:96` must be found and updated per new role
- ❌ No configuration-driven role/permission registry

### 1.3 Adding a New API Feature — 4/5

- ✅ Plug-and-play Blueprint registration — 2 files touched, no existing code modified
- ✅ `create_app` factory is well-structured with clean ordering
- ✅ Rate limiting is configurable per-route via `configure_auth_rate_limits`
- ✅ Centralized error handling inherited by all features
- ❌ No plugin registry or hook system — middleware/logging/caching requires editing `app.py`
- ❌ `configure_auth_rate_limits` reaches into `app.view_functions` by string key (fragile)

### 1.4 Frontend Extensibility — 3/5

- ✅ Generic `apiRequest` base client handles JSON, errors, and base URL
- ✅ Service-per-domain pattern established
- ❌ No service abstraction for common CRUD patterns
- ❌ Flat routes in `App.jsx` — every new page is a manual import
- ❌ No lazy loading or code-splitting
- ❌ AuthContext is a stub — role-based routing not implemented

### 1.5 Config Extensibility — 3/5

- ✅ Env-var-driven with sensible defaults
- ✅ `python-dotenv` included for `.env` files
- ❌ Single config class — no `DevelopmentConfig` / `ProductionConfig` hierarchy
- ❌ No config validation at startup
- ❌ Rate limit storage hardcoded to `memory://` — no production path

### 1.6 Plugin/Middleware Extensibility — 2/5

- ✅ Centralized extensions module (`db`, `migrate`, `jwt`, `limiter`)
- ✅ Naming convention metadata ensures consistent constraint names
- ❌ No `register_before_request`, no signal system, no plugin interface
- ❌ No blueprint-level middleware conventions
- ❌ `configure_security_logging` called unconditionally — no per-env toggle

### 1.7 Database Schema Evolution — 4/5

- ✅ Proper Alembic setup with Flask-Migrate
- ✅ Auto-skip empty revisions via `process_revision_directives`
- ✅ Deterministic constraint naming via `extensions.py:9-15`
- ✅ Clean `downgrade()` with proper drop order
- ❌ PostgreSQL ENUM types are additive-only — inflexible for role/status changes
- ❌ No data migration patterns — seed command lives outside Alembic

### Top Fix

A `PublishableMixin` + a `RoleRegistry` (method on `UserRole`) would push this score to 4+.

---

## 2. Modularity — 4.0/5

### 2.1 Backend Separation of Concerns — 4/5

- ✅ Routes are pure HTTP handlers — no SQL builders or template rendering
- ✅ Models define data only — no request handling or view logic
- ✅ Utils are truly cross-cutting helpers with no Flask coupling
- ❌ Auth route absorbs too much: credential parsing, validation, serialization, token creation, rate-limit wiring
- ❌ `configure_auth_rate_limits` in `routes/auth.py:134-140` is infrastructure leaked into a feature module
- ❌ Seed command imports multiple model types — couples to two domain areas

### 2.2 Blueprint Isolation — 4/5

- ✅ Each Blueprint is its own module with a `blueprint` export
- ✅ Centralized registration in `routes/__init__.py:11-19`
- ✅ Removing a Blueprint is a one-import-line fix
- ❌ Inconsistent `url_prefix` — only `auth.py` sets it, others don't
- ❌ Auth Blueprint is 140 lines; others are 3-line stubs — asymmetry will grow

### 2.3 Model Independence — 5/5

- ✅ Clean DAG — no circular dependencies
- ✅ String-based `db.relationship()` references — no import coupling between model files
- ✅ Consistent `ondelete="RESTRICT"` and `passive_deletes=True`
- ✅ Association table lives with the owning model
- ✅ Centralized `__all__` re-export in `models/__init__.py`
- ❌ None identified

### 2.4 Frontend Component Boundaries — 3/5

- ✅ Clean directory taxonomy: `components/layout/`, `components/content/`, `components/ui/`
- ✅ `Layout.jsx` uses `<Outlet />` — standard nested routing pattern
- ❌ Almost all components are empty stubs — cannot fully evaluate
- ❌ No component-level styling (global `styles.css` only)
- ❌ `components/content/` and `components/ui/` have only `.gitkeep`

### 2.5 Service Layer Isolation — 4/5

- ✅ Clean base client separation — `api.js` has zero domain knowledge
- ✅ Each domain gets its own service file
- ✅ Frozen stubs prevent accidental mutation
- ✅ `api.test.js` proves independent testability
- ❌ No auth token injection mechanism in the base client
- ❌ No request/response interceptors or middleware pattern

### 2.6 Context Separation — 3/5

- ✅ AuthContext is isolated from content/UI state
- ✅ Single context with single concern
- ❌ Hard-coded stub — always returns `{ user: null, token: null }`
- ❌ Not mounted in the app tree (`App.jsx` doesn't use `AuthProvider`)
- ❌ No pattern established for non-auth shared state

### 2.7 Infrastructure Boundaries — 5/5

- ✅ Three clearly separated services with distinct Dockerfiles and ports
- ✅ Health checks on all services with proper intervals and start periods
- ✅ Explicit dependency ordering via `condition: service_healthy`
- ✅ Scoped volumes — `postgres_data`, `frontend_node_modules`
- ✅ Environment variable passthrough — no secrets baked into images
- ❌ Source mount `.:/app` maps entire project root into backend container
- ❌ No network isolation between services

### 2.8 Cross-Cutting Concerns — 4/5

- ✅ Auth decorators centralized in one utility module
- ✅ Numeric role levels — clean integer comparisons
- ✅ `normalize_email` is a pure function with no Flask dependency
- ✅ Security logging isolated with dedicated logger
- ✅ Centralized error handling in `app.py`
- ❌ JWT error handlers register at import time (`utils/auth_helpers.py:22-44`)
- ❌ No shared validation framework (no Marshmallow/Pydantic)
- ❌ No shared serialization layer — `_public_user` is a private function in auth route

---

## 3. Maintainability — 4.3/5

### 3.1 Code Consistency — 4/5

- ✅ All models follow identical pattern — consistent column naming, `server_default`, `db.func.now()`, `onupdate`
- ✅ Enum definitions consistently use `values_callable` and `validate_strings`
- ✅ Constraint naming follows `extensions.py:9-15` convention
- ✅ All route files export a `blueprint` variable
- ✅ Backend uses `backend.` prefix for all imports
- ✅ Error responses use `jsonify(error="...")` uniformly
- ❌ Spec says singular filenames (`user.py`) but code uses plural (`users.py`)
- ❌ `TestConfig` class duplicated across 3 test files

### 3.2 Code Readability — 5/5

- ✅ Exceptionally small and focused files — app factory is 63 lines, models 18–80 lines, largest route 140 lines
- ✅ Helper functions are well-named and self-documenting
- ✅ No god objects — responsibilities cleanly separated
- ✅ Comments explain non-obvious logic without over-documenting
- ✅ Frontend `App.jsx` is only 30 lines

### 3.3 Test Coverage and Quality — 4/5

- ✅ 5 backend test files, ~1,444 lines total
- ✅ Tests run against real PostgreSQL with UUID-isolated databases
- ✅ Excellent use of `@pytest.mark.parametrize` for boundary testing
- ✅ Security-focused: credential leakage, timing attacks, stale token claims all tested
- ❌ No frontend component tests beyond App-level
- ❌ No unit tests for `normalize_email` in isolation
- ❌ Test config duplication across files

### 3.4 Documentation — 3/5

- ✅ README has exact Docker Compose commands for every operation
- ✅ `AGENTS.md` provides clear contributor guidelines
- ✅ `spec.md` is an excellent product specification
- ✅ `THIRD_PARTY_NOTICES.md` properly reproduces license notices
- ❌ **README is factually stale** — states "no domain schema, authentication, CRUD" which contradicts the actual codebase
- ❌ Missing `JWT_SECRET_KEY`, `SEED_SUPERADMIN_EMAIL`, `SEED_SUPERADMIN_PASSWORD` in `.env.example`
- ❌ No API contract documentation for existing endpoints
- ❌ No architecture guide or developer onboarding doc

### 3.5 Error Handling Consistency — 5/5

- ✅ Uniform `{"error": "message"}` JSON shape across all API errors
- ✅ Global HTTP exception handler distinguishes API vs non-API paths
- ✅ 500 handler returns generic message — no traceback exposure
- ✅ Security-first auth errors — same "Invalid credentials" regardless of account existence
- ✅ Timing-safe password verification before role checking
- ✅ Security logging sanitizes all inputs — never logs emails, passwords, hashes, or tokens
- ✅ Signup uses both pre-commit check and `IntegrityError` catch for race conditions

### 3.6 Dependency Health — 5/5

- ✅ All backend deps pinned to exact versions — Flask 3.1.3, SQLAlchemy 2.0.52, Alembic 1.19.2
- ✅ All frontend deps pinned — React 19.3.0, Vite 8.2.2, React Router 7.18.3
- ✅ All packages current, well-maintained, permissively licensed
- ✅ Docker base images current — `python:3.13-slim`, `node:24-slim`, PostgreSQL 18
- ❌ `python-dotenv` listed but no explicit `load_dotenv()` call — implicit loading may not work everywhere

### 3.7 Configuration Management — 4/5

- ✅ Clean `Config` class with env-var overrides and sensible defaults
- ✅ `JWT_SECRET_KEY` falls back to `SECRET_KEY` for local dev
- ✅ Compose passes all necessary env vars — works without `.env` file
- ✅ CORS properly scoped to `/api/*` with exact origin
- ❌ Missing `.env.example` entries
- ❌ `RATELIMIT_STORAGE_URI` set in both `config.py:18` and `app.py:19` — redundancy
- ❌ No feature flags or logging config

### 3.8 Technical Debt Indicators — 4/5

- ✅ No commented-out code anywhere in production
- ✅ No TODO comments in production — tracked in `TODO.md`
- ✅ Stubs are intentional and documented
- ✅ Workarounds are explicitly documented (security logging, limiter retention)
- ❌ Stale README is primary documentation debt
- ❌ Frontend components are almost entirely placeholders (expected for this stage)

### 3.9 DB Migration Hygiene — 5/5

- ✅ Single clean migration covering entire domain schema
- ✅ Correct ENUM handling with `checkfirst=True`
- ✅ Complete and correct `downgrade()` with proper drop order
- ✅ Deterministic constraint naming prevents migration conflicts
- ✅ Comprehensive migration tests verify upgrade/downgrade round-trip
- ✅ Model contract tests ensure ORM metadata matches expectations

---

## 4. Priority Recommendations

| #  | Action | Dimension     | Impact | Effort |
|----|--------|---------------|--------|--------|
| 1  | Add `PublishableMixin` for shared content model columns | Expandability | High   | Low    |
| 2  | Move role levels into `UserRole` as a classmethod | Expandability | High   | Low    |
| 3  | Update README to reflect current project state | Maintainability | High | Low    |
| 4  | Add missing `.env.example` entries | Maintainability | Medium | Low    |
| 5  | Extract shared test config into conftest | Maintainability | Medium | Low    |
| 6  | Add `register_extension()` hook in `create_app` | Expandability | Medium | Medium |
| 7  | Consolidate rate-limit wiring out of auth route | Modularity  | Medium | Medium |
| 8  | Add lazy loading + route config file for frontend | Expandability | Medium | Medium |
| 9  | Add validation framework (Marshmallow/Pydantic) | Modularity  | Medium | Medium |
| 10 | Add API contract docs to README | Maintainability | Medium | Low    |

---

## 5. Appendix: Files Reviewed

### Backend

- `backend/app.py`, `backend/config.py`, `backend/extensions.py`, `backend/commands.py`
- `backend/routes/__init__.py`, `backend/routes/auth.py`, `backend/routes/articles.py`, `backend/routes/announcements.py`, `backend/routes/categories.py`, `backend/routes/media.py`, `backend/routes/pages.py`, `backend/routes/tags.py`, `backend/routes/users.py`
- `backend/models/__init__.py`, `backend/models/users.py`, `backend/models/articles.py`, `backend/models/announcements.py`, `backend/models/categories.py`, `backend/models/media.py`, `backend/models/pages.py`, `backend/models/tags.py`
- `backend/utils/auth_helpers.py`, `backend/utils/validation.py`, `backend/utils/security_logging.py`
- `backend/requirements.txt`

### Frontend

- `frontend/src/App.jsx`, `frontend/src/styles.css`
- `frontend/src/services/api.js`, `frontend/src/services/articles.js`, `frontend/src/services/auth.js`, `frontend/src/services/announcements.js`
- `frontend/src/context/AuthContext.jsx`
- `frontend/src/routes/ProtectedRoute.jsx`
- `frontend/src/components/layout/Layout.jsx`
- `frontend/src/pages/public/Home.jsx`
- `frontend/package.json`

### Infrastructure & Docs

- `compose.yaml`, `backend/Dockerfile`, `frontend/Dockerfile`
- `migrations/alembic.ini`, `migrations/env.py`
- `README.md`, `AGENTS.md`, `TODO.md`, `spec.md`, `THIRD_PARTY_NOTICES.md`
