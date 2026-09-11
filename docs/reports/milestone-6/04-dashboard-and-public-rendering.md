# Milestone 6 Dashboard and Public Rendering

## Status: in progress

Article-save correction: the editor sends explicit writable fields and one body representation, strips resolved image metadata from requests, preserves block order and publication status, and exposes load failures with retry. Existing text blocks can be edited individually without removing picture references. Repeated backend block replacement flushes removed rows inside the transaction before reusing their positions.

Verification to date: 128 backend tests, 49 frontend tests, and the frontend production build passed in Compose. Regression coverage includes repeated block replacement/reordering/removal, duplicate-slug rollback behavior, published article metadata saves retaining pictures, role-specific editor states, dashboard ownership guards, list filtering, and editor load failures. Authenticated Playwright acceptance remains pending because no non-production dashboard credentials are configured.

The first dashboard slice replaces the placeholder with authenticated article management routes. Publishers can list their own articles, create a draft, edit a draft, and submit it for review. The dashboard retains loading, error, empty, and retry states, and unknown dashboard URLs remain behind the authentication boundary.

The article workflow now enforces dashboard ownership for Publishers, renders submitted and published articles read-only to their authors, and exposes explicit Admin/Superadmin Publish, Return to draft, and Unpublish actions. The list has a role-scoped status filter. Save requests are guarded against duplicate in-flight actions, and duplicate-slug errors during block replacement roll back the complete article update rather than escaping as a server error.

The next additions to this stage are shared picture-block editing and previews, announcement and page workflows, media upload/picking, and public picture-block rendering. Authenticated Playwright acceptance remains pending.
