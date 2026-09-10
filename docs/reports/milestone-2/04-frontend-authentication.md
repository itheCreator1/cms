# Milestone 2 Frontend Authentication

## Status: implemented; final acceptance pending

Frontend authentication is implemented against the completed backend foundation.

Delivered:

- Access tokens persist under `cms_access_token` and restore through `/api/me`.
- Invalid 401 sessions are cleared; logout clears memory and storage.
- The shared API client attaches bearer tokens automatically.
- Regular and isolated Superadmin auth-service calls are separate.
- Protected routes enforce the numeric Visitor/Publisher/Admin/Superadmin hierarchy for frontend navigation.
- Regular and visually distinct Superadmin login pages are working.
- Frontend tests cover persistence, authorization headers, logout, restoration, routing, and both login screens.

Final milestone acceptance remains pending until the complete Compose verification sequence is recorded.
