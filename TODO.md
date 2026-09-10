# CMS TODO

Milestone 1—the Dockerized Flask, React, and PostgreSQL project skeleton—is complete. The following work remains for the full CMS described in `spec.md`.

## Backend

- [x] Implement the User, Article, Announcement, Page, Category, Tag, and Media domain models.
- [x] Add model relationships, foreign keys, slug indexes, status values, timestamps, and the article–tag association.
- [x] Generate, review, and apply the first schema migration.
- [x] Implement public signup and regular login with password hashing and JWT issuance.
- [x] Implement the separate superadmin login endpoint with stricter rate limiting and attempt logging.
- [x] Add reusable authentication and numeric role-level authorization helpers.
- [x] Enforce publisher ownership rules and Admin/Superadmin permission boundaries for articles, announcements, and pages.
- [x] Implement CRUD APIs for articles, announcements, and pages.
- [ ] Implement CRUD APIs for categories, tags, media, and users.
- [x] Restrict unauthenticated article, announcement, and page responses to published records.
- [x] Add request validation, consistent JSON errors, and appropriate HTTP status codes for the authentication foundation.
- [ ] Implement media uploads, local file storage, and returned media URLs.
- [x] Add a seed command that creates a Superadmin and sample categories using credentials from environment variables.
- [x] Add the seed and JWT variables to `.env.example` without committing credentials.

## Frontend

- [x] Replace the inert auth context with JWT and current-user state, including local-storage restoration and logout.
- [x] Attach authentication tokens automatically in the shared API client.
- [x] Replace the unconditional dashboard redirect with role-aware protected routes.
- [x] Implement regular and visually distinct Superadmin login flows against their separate endpoints.
- [ ] Fetch and render published announcements and articles on the homepage.
- [ ] Fetch and render public article, announcement, and page routes.
- [ ] Implement article and announcement API services and the remaining content, taxonomy, media, and user services.
- [ ] Build the role-aware dashboard and editable content lists.
- [ ] Add article and announcement editors with draft, review, publish, and unpublish workflows.
- [ ] Add category and tag management, the media library/uploader, and user administration screens.
- [ ] Show dashboard sections and actions according to Publisher, Admin, and Superadmin permissions.

## Testing

- [x] Add model and migration tests against PostgreSQL.
- [x] Test signup, login, JWT validation, Superadmin isolation, and role hierarchy behavior.
- [x] Test ownership and authorization boundaries for article, announcement, and page operations.
- [ ] Test ownership and authorization boundaries for taxonomy, media, and user operations.
- [x] Test seed validation, idempotency, and collision handling.
- [x] Test content-core CRUD validation and public-content filtering.
- [ ] Test taxonomy/user CRUD validation and uploads.
- [x] Test frontend authentication persistence, protected routes, role-aware navigation, and both login screens.
- [ ] Test public content and dashboard workflows.
- [ ] Add end-to-end coverage for critical public and authenticated user journeys.
- [x] Run the full Compose acceptance sequence after each completed milestone.

## Delivery

- [x] Expand the README as working CMS commands and operational requirements are introduced.
- [ ] Configure a Git remote and push the existing local commits when ready.
