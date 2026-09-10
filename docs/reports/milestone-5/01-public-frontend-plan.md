# Milestone 5 Public Frontend Plan

## Status: active

Milestone 5 replaces the public placeholders with a complete reading experience while preserving the existing Flask REST contracts and authenticated dashboard boundary.

## Deliverables

- An editorial newspaper-style shell and responsive public homepage.
- Published announcements and articles loaded through focused public API services.
- A lead story, article grid, category labels, featured images, and deterministic excerpts.
- Working article, announcement-index, and static-page routes.
- Accessible loading, empty, not-found, failure, and retry states.
- Safe plain-text body rendering with paragraphs and line breaks preserved.
- Anonymous public requests that are unaffected by a stored or expired JWT.
- Backend-relative media URL resolution for uploaded featured images.
- Vitest and Testing Library coverage for public services and reading workflows.

## Architecture decisions

The frontend composes the public experience from the existing article, announcement, page, and category endpoints. No aggregate homepage endpoint or database migration is introduced. Homepage resources load independently so an announcement or taxonomy failure does not suppress available articles.

Public service calls explicitly omit bearer authentication even when `cms_access_token` exists. This keeps published content available when a browser contains an expired token. Article category names are optional enrichment; the numeric category identifier is not displayed when metadata is unavailable.

Stored content is rendered as text, never injected HTML. Markdown parsing, sanitization, rich provider embeds, pagination, search, dashboard screens, and site-wide settings remain later work.

## Delivery sequence

1. Define and implement public API-client and service contracts using test-driven development.
2. Define and implement reusable public content components and route behavior using test-driven development.
3. Update the README and TODO tracker, then record implementation and final verification reports.
4. Verify the full frontend and backend suites, production build, Compose health, and public HTTP routes.

Each stage is committed separately with explicit paths. The deleted architecture audit and untracked `.diagram-design` are user-owned state and remain untouched.
