# Milestone 3 Content Core Plan

## Status: complete

Milestone 3 establishes the backend content-management boundary before frontend content workflows are added.

## Deliverables

- Centralized ownership, role, and visibility rules for content operations.
- REST JSON APIs for articles, announcements, and pages.
- Published-only anonymous reads and role-aware authenticated reads.
- Publisher ownership enforcement for draft articles and announcements.
- Admin and Superadmin publication and cross-owner management.
- PostgreSQL-backed tests for CRUD, validation, authorization, and visibility.

Publishers do not manage pages and cannot edit or delete submitted or published content. Admins and Superadmins manage all three content types and control publication. Invalid bearer tokens continue to return the authentication API's consistent JSON `401` response rather than being treated as anonymous.

Review found that announcement review submission required a `pending_review` enum value that was absent from the original schema. A separate reviewed Alembic revision adds that value and supports upgrade/downgrade testing.

## Deferred

- Category and tag management APIs.
- Media CRUD and file uploads.
- User administration.
- Public content pages and dashboard/editor workflows.
