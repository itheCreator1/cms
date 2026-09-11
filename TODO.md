# CMS TODO

Milestone 1—the Dockerized Flask, React, and PostgreSQL project skeleton—is complete. The following work remains for the full CMS described in `spec.md`.

Milestone 4—taxonomy CRUD, secure image uploads, external media links, and guarded user administration—is complete. Markdown rendering, rich provider embeds, and non-image uploads remain later work.

Milestone 5—the editorial public homepage and published article, announcement, and page routes—is complete. The authenticated dashboard remains the next delivery area.

The reusable frontend foundation is the prerequisite for Milestone 6. It establishes the shared layouts, navigation, controls, theme tokens, and homepage composition conventions that the dashboard and publisher-picture work will use.

Milestone 6 has begun with ordered text-and-picture content blocks and a compatibility migration. Publisher media permissions, private image delivery, dashboard workflows, public picture rendering, and final acceptance remain.

## Frontend stabilization gate

- [x] Restore the normal Vite development command and restart the frontend.
- [x] Run Compose frontend tests (42), backend tests (119), and frontend build; verify fresh Firefox startup and public empty/not-found states.
- [ ] Capture the affected browser’s failed `PageView.jsx` request and console error, reproduce the failure, and add a regression test before any application behavior fix.
- [ ] Confirm the affected browser renders the homepage, both login screens, and published detail routes without failed application modules or uncaught startup errors before starting Milestone 6. See [acceptance evidence](docs/reports/frontend-stabilization.md).

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
- [x] Add a seed command that creates a Superadmin and sample categories using credentials from environment variables.
- [x] Add the seed and JWT variables to `.env.example` without committing credentials.

## Frontend

- [x] Build the reusable frontend foundation: `PublicLayout`, `AuthLayout`, and `DashboardLayout`; shared `Header`, `Navigation`, and `Footer`; reusable `Button` and `FormField` controls; homepage presentation components and `useHomeContent`.
- [x] Complete the stylesheet migration: retain theme tokens and the global reset in `frontend/src/styles.css`, then move the remaining legacy layout, page, and content-card rules into co-located CSS Modules.
- [x] Replace the inert auth context with JWT and current-user state, including local-storage restoration and logout.
- [x] Attach authentication tokens automatically in the shared API client.
- [x] Replace the unconditional dashboard redirect with role-aware protected routes.
- [x] Implement regular and visually distinct Superadmin login flows against their separate endpoints.
- [x] Fetch and render published announcements and articles on the homepage.
- [x] Fetch and render public article, announcement, and page routes.
- [x] Implement public article, announcement, page, and category API services.
- [ ] Implement dashboard content, tag, media, and user API services.
- [ ] Build the role-aware dashboard and editable content lists.
- [ ] Add article and announcement editors with draft, review, publish, and unpublish workflows.
- [ ] Add category and tag management, the media library/uploader, and user administration screens.
- [ ] Show dashboard sections and actions according to Publisher, Admin, and Superadmin permissions.
- [ ] Add Superadmin-authorized site-wide settings persistence, API validation, and dashboard management screens.

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
- [ ] Test dashboard workflows.
- [ ] Add end-to-end coverage for critical public and authenticated user journeys.
- [x] Run the full Compose acceptance sequence after each completed milestone.

## Delivery

- [x] Expand the README as working CMS commands and operational requirements are introduced.
- [ ] Configure a Git remote and push the existing local commits when ready.
