# Milestone 3 Content Core Plan

## Status: in progress

Milestone 3 establishes the backend content-management boundary before frontend content workflows are added.

## Deliverables

- Centralized ownership, role, and visibility rules for content operations.
- REST JSON APIs for articles, announcements, and pages.
- Published-only anonymous reads and role-aware authenticated reads.
- Publisher ownership enforcement for draft articles and announcements.
- Admin and Superadmin publication and cross-owner management.
- PostgreSQL-backed tests for CRUD, validation, authorization, and visibility.

Publishers do not manage pages and cannot edit or delete submitted or published content. Admins and Superadmins manage all three content types and control publication. Invalid bearer tokens continue to return the authentication API's consistent JSON `401` response rather than being treated as anonymous.

The existing domain schema supports this milestone, so no Alembic revision is expected. Any discovered schema requirement must be handled through a separately reviewed migration.

## Deferred

- Category and tag management APIs.
- Media CRUD and file uploads.
- User administration.
- Public content pages and dashboard/editor workflows.
