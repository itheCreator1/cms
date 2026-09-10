# Milestone 2 Backend Foundation Report

## Status

The Milestone 2 backend foundation is complete and independently reviewed. Frontend authentication and the broader milestone documentation/acceptance pass have not started.

## Delivered

- Complete SQLAlchemy domain schema for users, articles, announcements, pages, categories, tags, media, and article–tag relationships.
- Stable enum, foreign-key, uniqueness, and slug-index definitions with restrictive delete behavior.
- Reviewed Alembic revision supporting PostgreSQL upgrade, downgrade, and re-upgrade.
- Werkzeug password hashing and verification.
- Public Visitor signup, regular Visitor/Publisher/Admin login, isolated Superadmin login, and authenticated identity loading.
- Bearer JWT access tokens with string user identity, role claims, configurable expiry, and database-authoritative role checks.
- Centralized numeric role hierarchy and reusable authentication/authorization helpers.
- Per-client-IP login limits of 20 attempts/minute for regular login and 5 attempts/minute for Superadmin login.
- Sanitized Superadmin audit logging for successful, denied, malformed, and rate-limited attempts.
- Consistent JSON API errors, including authentication, authorization, method, rate-limit, and sanitized internal-error responses.
- Environment-driven, idempotent Superadmin/category seed command with conflict-safe behavior.
- MIT license notices for Flask-JWT-Extended 4.7.4 and Flask-Limiter 4.1.1.

## Security review

Independent review identified and the follow-up commit corrected:

- hostile, control-character, and overlength email input reaching PostgreSQL;
- category seed collisions involving separate matching name and slug rows;
- HTML method errors and unsanitized unexpected API failures;
- rate-limiter state leaking between Flask application instances;
- missing authorization-boundary, stale-role, and audit-log regression coverage.

The scoped re-review approved the fixes with no remaining Critical, Important, or Minor findings.

## Verification

Final verification on 2026-09-10 used the canonical Compose runtime:

```text
docker compose run --rm backend pytest backend/tests -q
89 passed in 11.62s

docker compose config --quiet
exit 0
```

Model/migration verification also confirmed Alembic model parity and PostgreSQL upgrade/downgrade behavior. Temporary test databases were isolated from the development database and removed after execution.

## Atomic commits

- `590e4c9 feat(backend): add CMS domain schema`
- `4a9d71c feat(backend): add authentication foundation`
- `0dce5c6 fix(backend): harden authentication boundaries`

The project-wide agent guide was recorded separately as `5b521b4 docs: add project agent guide`.

## Deferred

- Frontend authentication, token restoration, login screens, and role-aware protected routes.
- Content, taxonomy, media, and user-management CRUD and ownership enforcement.
- Upload handling, public-content APIs, refresh/revocation, and distributed rate-limit storage.
- `.env.example`, README operational instructions, full Milestone 2 acceptance verification, and the remaining milestone reports.
