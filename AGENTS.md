# Project Agent Guide

These instructions apply to the entire repository.

- Treat `spec.md` as the product source of truth and `TODO.md` as the progress tracker.
- Use Docker Compose as the canonical runtime and run tests inside service containers.
- Preserve the Flask application factory, Blueprints, SQLAlchemy, Alembic, React Router, and shared API-client architecture.
- Use test-driven development for application behavior and add regression tests for every fix.
- Never use `db.create_all()` for managed schema changes. Generate, review, test, and commit Alembic revisions.
- Never commit secrets, credentials, uploaded media, caches, or generated build artifacts.
- Enforce authorization on the backend. Frontend visibility rules are never security controls.
- Use numeric role levels and centralized authentication and authorization helpers.
- Return consistent JSON errors without exposing credentials, password hashes, tokens, or internal exceptions.
- Prefer maintained, permissively licensed dependencies and retain notices when adapting third-party code.
- Keep route handlers and React components focused and single-purpose.
- Update `README.md` and `TODO.md` whenever functionality or operational commands change.
- Preserve unrelated user changes and create separate focused commits for documentation, models and migrations, backend authentication, frontend authentication, and tests.
