# Milestone 2 Final Verification

## Status: complete

Milestone 2 backend and frontend authentication acceptance is complete. Content CRUD, ownership enforcement, uploads, and the full dashboard remain future milestones.

## Backend evidence available

```text
docker compose run --rm backend pytest backend/tests -q
89 passed in 7.73s

docker compose run --rm frontend npm test -- --run
28 passed

docker compose run --rm frontend npm run build
vite build exited 0

docker compose config --quiet
exit 0
```

The model/migration and backend authentication tests ran against PostgreSQL; the 89-test backend suite includes migration upgrade/downgrade and seed coverage. The frontend suite covers token storage, bearer headers, restoration, logout, role-aware routing, and both login screens.

Compose health checks on 2026-09-10:

```text
cms-db-1        Up (healthy)
cms-backend-1   Up (healthy)
cms-frontend-1  Up (healthy)
```

Host HTTP smoke checks used one disposable Visitor account and removed it afterward:

```text
GET  /api/health                  200 {"status":"ok"}
GET  /api/does-not-exist          404 {"error":"Not found"}
POST /api/signup                  201
POST /api/login                   200 (access token returned)
GET  /api/me with bearer token    200 (Visitor identity)
POST /api/superadmin-login        401 for Visitor
GET  /api/me without token        401 {"error":"Authentication required"}
```

## Required before milestone completion

- Frontend authentication and protected routing are complete.
- `.env.example`, README authentication/seeding/migration instructions, and TODO tracking are current.
- Backend/frontend suites and the frontend production build pass in Compose.
- PostgreSQL migration round-trip and Alembic model-parity tests pass.
- The complete stack reports healthy services.
- Host HTTP smoke tests pass for health, signup, regular login, Superadmin isolation, authenticated identity, and JSON errors.
