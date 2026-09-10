# Milestone 2 Backend Authentication

## Delivered

- Pinned Flask-JWT-Extended 4.7.4 and Flask-Limiter 4.1.1 with MIT notices.
- Visitor signup with normalized, bounded email validation and password hashing.
- Separate regular and Superadmin login endpoints returning access tokens and public user identities.
- Bearer JWTs with string user identity, role claim, and configurable expiry.
- Authenticated identity endpoint and database-authoritative user/role loading.
- Central numeric role hierarchy and reusable authentication/authorization decorators.
- Regular-login limit of 20 attempts/minute and Superadmin-login limit of 5 attempts/minute per immediate client IP.
- Sanitized Superadmin audit records for every success, denial, malformed request, and rate-limit event.
- Consistent JSON authentication, authorization, method, rate-limit, and sanitized internal-error responses.
- Environment-driven idempotent seed command for one Superadmin identity and initial categories.

## Security properties

Regular login excludes Superadmin accounts. Superadmin login verifies a found password before checking its role, and all invalid credential/role outcomes use a generic response. Protected requests reload the user so deletion, promotion, and demotion take effect without trusting stale token claims.

Rate-limit state is isolated per Flask application instance. Forwarded headers are not blindly trusted. In-memory storage remains intentionally process-local for this milestone.

## Review findings resolved

The first review reproduced unsafe overlength/control-character emails, a valid category seed collision, HTML API method errors, cross-application limiter state leakage, and missing boundary/audit regression cases. The hardening commit fixed each issue. Scoped re-review approved the result with no remaining findings and independently ran 25 focused tests successfully.

## Final verification

```text
docker compose run --rm backend pytest backend/tests -q
89 passed in 11.62s

docker compose config --quiet
exit 0
```

## Atomic commits

- `4a9d71c feat(backend): add authentication foundation`
- `0dce5c6 fix(backend): harden authentication boundaries`
