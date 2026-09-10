# Milestone 4 Backend Administration

## Status: complete

The backend now exposes public category and tag reads with Admin-only mutation, an Admin-managed media library, and role-scoped user administration. Referenced records are protected by restrictive foreign keys and return JSON conflicts instead of cascading or silently detaching content.

Media records distinguish uploaded and external sources. Uploaded JPEG, PNG, WebP, and non-animated GIF images are size-checked, decoded, re-encoded without metadata, and stored under generated names through a local-storage adapter. External HTTPS links are normalized and classified without outbound requests or raw embed HTML. The local adapter uses a persistent Compose volume and leaves a clear boundary for future object storage.

Admins can manage Publisher accounts. Superadmins can manage every role but cannot delete or demote the account backing their active session. JWTs now identify their login channel, preventing an account promoted from Admin to Superadmin from gaining Superadmin authority through an old regular-login token.

The reviewed `91c4d2e7f8a0` Alembic revision adds source-aware media fields and a unique storage key while preserving legacy media rows across upgrade and downgrade.

## Deferred extensions

- Markdown parsing and sanitized rendering.
- oEmbed and provider-specific renderer adapters.
- Video, audio, document, animated-image, and SVG uploads.
- Cloud storage, malware scanning, and background transcoding.
- Public and dashboard frontend media workflows.
