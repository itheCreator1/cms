# Milestone 5 Final Verification

## Status: complete

Verification was run on 2026-09-10 using the canonical Docker Compose services.

## Automated checks

- Backend: `docker compose exec backend pytest -q backend/tests` — 119 passed.
- Frontend: `docker compose exec frontend npm test` — 9 files and 41 tests passed.
- Production build: `docker compose exec frontend npm run build` — 48 modules transformed successfully.
- Compose: `docker compose config --quiet` succeeded and the database, backend, and frontend services reported healthy.
- Migrations: `flask db current` and `flask db heads` both reported `91c4d2e7f8a0 (head)`.

## Public workflow coverage

The frontend suite verifies newest-first article and announcement ordering, lead-story selection, category enrichment, backend-relative featured-image URLs, meaningful image alternative text, empty collections, independent homepage failures, retry behavior, route-level not-found handling, and literal rendering of stored markup.

Service tests verify that public article, announcement, page, and category requests omit `Authorization` even when `cms_access_token` contains a stale token.

## Host smoke checks

Host requests returned `200` for:

- `/api/health`, with `{"status":"ok"}`;
- `/api/articles`, `/api/announcements`, and `/api/categories`;
- frontend `/`, `/articles/smoke-route`, `/announcements`, and `/pages/about`.

The development database contained no public content during the host smoke run, so the collection responses were empty and no persistent smoke records or credentials were created. Populated rendering is covered by deterministic route-level tests.

## Result

Milestone 5 satisfies the approved public-frontend plan without backend or schema changes. The authenticated dashboard remains the next delivery area.
