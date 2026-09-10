# Milestone 1 Backend Foundation

## Delivered

- Importable `backend.app:create_app` Flask application factory.
- Environment-backed configuration for the database, frontend origin, and Flask secret.
- Initialized Flask-SQLAlchemy and Flask-Migrate extensions.
- Feature Blueprint modules for authentication, articles, announcements, pages, media, categories, tags, and users.
- `GET /api/health` with the exact compact JSON contract `{"status":"ok"}`.
- Configured-origin CORS behavior for `/api/*`.
- JSON `404` responses for unknown API routes while retaining Flask HTML responses outside `/api`.
- Tracked Alembic configuration without a fabricated Milestone 1 domain revision.

## Tests

The initial backend suite covered application-factory creation, health behavior, compact JSON in debug mode, CORS allow/deny behavior, API/non-API 404 behavior, and imports for every placeholder route and model module.

At the Milestone 2 baseline check, the unchanged Milestone 1 backend suite reported:

```text
22 passed in 0.81s
```

## Commit

`2c14c9a feat(backend): scaffold Flask API and migrations`
