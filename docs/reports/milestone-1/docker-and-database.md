# Milestone 1 Docker and Database Runtime

## Delivered

- PostgreSQL 18 service with persistent data volume and `pg_isready` health check.
- Flask backend image, source bind mount, exposed port 5000, and HTTP health check.
- Vite frontend image, source bind mount, container-managed `node_modules` volume, exposed port 5173, and HTTP health check.
- Dependency ordering based on service health.
- Root `.env.example` with local Compose defaults and placeholders.
- Root `.dockerignore` for smaller, safer build contexts.

Docker Compose is the canonical runtime. The documented lifecycle includes build/start, background operation, status/log inspection, stop/start with persistent volumes, normal teardown, intentional volume deletion, rebuilds, containerized tests, frontend production builds, and migration inspection.

## Database migration boundary

Milestone 1 tracked the Alembic environment but intentionally left `migrations/versions/` without a domain revision. Normal setup uses `flask db upgrade`; `flask db init` remains a one-time maintainer operation.

## Commit

`1ae2cc9 chore: add Docker Compose development stack`
