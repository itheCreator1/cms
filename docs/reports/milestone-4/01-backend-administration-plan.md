# Milestone 4 Backend Administration Plan

## Status: active

Milestone 4 completes the backend administration boundary before public and dashboard frontend work continues.

## Deliverables

- Public category and tag reads with Admin-only taxonomy mutation.
- A source-aware media model for local uploads and external HTTPS links.
- Secure JPEG, PNG, WebP, and non-animated GIF uploads through a replaceable storage adapter.
- A persistent local-media Compose volume and public file-serving endpoint.
- Admin management of Publisher accounts and guarded Superadmin management of every role.
- Superadmin login-channel enforcement so regular tokens cannot gain Superadmin authority after an account promotion.
- PostgreSQL-backed API, authorization, storage, and migration tests.

## Security and integrity decisions

Uploaded images are limited to 10 MB and 40 megapixels, decoded and re-encoded with Pillow, stripped of metadata, and stored under generated UUID names. SVG and animated GIF files are rejected. External media must use HTTPS, is classified without making an outbound request, and cannot contain raw embed HTML.

Database foreign keys remain restrictive. Referenced categories, tags, media, and users return a conflict response on deletion; dependent content is never cascaded or silently detached. A Superadmin cannot delete or demote the account backing the current session, and the database must retain at least one Superadmin.

## Deferred

- Markdown parsing and sanitized frontend rendering.
- oEmbed lookups and provider-specific rendering adapters.
- Video, audio, document, and SVG uploads.
- Cloud/object storage, malware scanning, and background media processing.
- Public and dashboard frontend media workflows.
