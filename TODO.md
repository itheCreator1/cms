# CMS TODO

The mandatory CMS work in `spec.md` is complete. Markdown rendering, rich provider embeds, and non-image uploads remain in the future backlog.

Milestone 4—taxonomy CRUD, secure image uploads, external media links, and guarded user administration—is complete. Markdown rendering, rich provider embeds, and non-image uploads remain later work.

Milestone 5—the editorial public homepage and published article, announcement, and page routes—is complete.

The reusable frontend foundation supplies shared layouts, navigation, controls, theme tokens, and homepage composition conventions.

Milestone 6 is complete for ordered text-and-picture blocks, publisher media permissions, article/announcement/page dashboard workflows, draft/review/publication controls, picture upload/reuse, authenticated previews, and public picture rendering. The originally affected browser was confirmed working, and Chromium/Firefox Compose acceptance passed.

## Frontend stabilization gate

- [x] Restore the normal Vite development command and restart the frontend.
- [x] Run Compose frontend tests (72), backend tests (138), and frontend build; verify fresh Firefox startup and public empty/not-found states.
- [x] The originally affected browser now renders correctly; no application behavior fix was needed because the reported failure could not be reproduced after restoring the normal Vite command.
- [x] Run and record the Compose browser suite covering startup, both login flows, publishing, public image visibility, unpublishing, published detail routes, administration, role boundaries, and public settings. Chromium and Firefox: 10 passed. See [acceptance evidence](docs/reports/milestone-6/05-frontend-stabilization-acceptance.md).

## Backend

- [x] Implement the User, Article, Announcement, Page, Category, Tag, and Media domain models.
- [x] Add model relationships, foreign keys, slug indexes, status values, timestamps, and the article–tag association.
- [x] Generate, review, and apply the first schema migration.
- [x] Implement public signup and regular login with password hashing and JWT issuance.
- [x] Implement the separate superadmin login endpoint with stricter rate limiting and attempt logging.
- [x] Add reusable authentication and numeric role-level authorization helpers.
- [x] Enforce publisher ownership rules and Admin/Superadmin permission boundaries for articles, announcements, and pages.
- [x] Implement CRUD APIs for articles, announcements, and pages.
- [x] Implement CRUD APIs for categories, tags, media, and users.
- [x] Restrict unauthenticated article, announcement, and page responses to published records.
- [x] Add request validation, consistent JSON errors, and appropriate HTTP status codes for the authentication foundation.
- [x] Implement media uploads, local file storage, and returned media URLs.
- [x] Add ordered content blocks with a compatibility migration for existing plain-text bodies.
- [x] Allow Publisher image uploads with ownership checks and publication-aware private file delivery.
- [x] Add a seed command that creates a Superadmin and sample categories using credentials from environment variables.
- [x] Add the seed and JWT variables to `.env.example` without committing credentials.

## Frontend

- [x] Correct article save payloads, retain existing picture blocks and status, and show editor load errors with retry.

- [x] Build the reusable frontend foundation: `PublicLayout`, `AuthLayout`, and `DashboardLayout`; shared `Header`, `Navigation`, and `Footer`; reusable `Button` and `FormField` controls; homepage presentation components and `useHomeContent`.
- [x] Complete the stylesheet migration: retain theme tokens and the global reset in `frontend/src/styles.css`, then move the remaining legacy layout, page, and content-card rules into co-located CSS Modules.
- [x] Replace the inert auth context with JWT and current-user state, including local-storage restoration and logout.
- [x] Attach authentication tokens automatically in the shared API client.
- [x] Replace the unconditional dashboard redirect with role-aware protected routes.
- [x] Implement regular and visually distinct Superadmin login flows against their separate endpoints.
- [x] Fetch and render published announcements and articles on the homepage.
- [x] Fetch and render public article, announcement, and page routes.
- [x] Implement public article, announcement, page, and category API services.
- [x] Implement dashboard content, tag, and media API services.
- [x] Add a shared user-management API service.
- [x] Build the role-aware dashboard and editable content lists.
- [x] Add article and announcement editors with draft, review, publish, and unpublish workflows.
- [x] Add category and tag management, the media library/uploader, and user administration screens.
- [x] Show dashboard sections and actions according to Publisher, Admin, and Superadmin permissions.
- [x] Add Superadmin-authorized site-wide settings persistence, API validation, and dashboard management screens.

## Testing

- [x] Add model and migration tests against PostgreSQL.
- [x] Test signup, login, JWT validation, Superadmin isolation, and role hierarchy behavior.
- [x] Test ownership and authorization boundaries for article, announcement, and page operations.
- [x] Test ownership and authorization boundaries for taxonomy, media, and user operations.
- [x] Test seed validation, idempotency, and collision handling.
- [x] Test content-core CRUD validation and public-content filtering.
- [x] Test taxonomy/user CRUD validation and uploads.
- [x] Test frontend authentication persistence, protected routes, role-aware navigation, and both login screens.
- [x] Test public content workflows, failures, retries, ordering, and safe body rendering.
- [x] Test dashboard workflows.
- [x] Expand end-to-end coverage to taxonomy, media upload and links, user-role boundaries, and settings changes.
- [x] Run the full Compose acceptance sequence after each completed milestone.

## Delivery

- [x] Expand the README as working CMS commands and operational requirements are introduced.
- [x] Configure the `origin` Git remote.
- [x] Keep the completed branch committed locally; pushing is outside this delivery.
