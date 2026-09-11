# Milestone 6 Dashboard and Public Rendering

## Status: implementation complete; browser acceptance pending

Article-save correction: the editor sends explicit writable fields and one body representation, strips resolved image metadata from requests, preserves block order and publication status, and exposes load failures with retry. Existing text blocks can be edited individually without removing picture references. Repeated backend block replacement flushes removed rows inside the transaction before reusing their positions.

Verification: 128 backend tests, 65 frontend tests, the frontend production build, API health, frontend health, and Alembic head alignment passed in Compose. Regression coverage includes repeated block replacement/reordering/removal, duplicate-slug rollback behavior, published article metadata saves retaining pictures, role-specific editor states, dashboard ownership guards, list filtering, multipart request headers, picture uploads, public inline-picture rendering, announcement/page workflows, and editor load failures. Authenticated browser acceptance remains pending for the originally affected browser profile.

The first dashboard slice replaces the placeholder with authenticated article management routes. Publishers can list their own articles, create a draft, edit a draft, and submit it for review. The dashboard retains loading, error, empty, and retry states, and unknown dashboard URLs remain behind the authentication boundary.

The article workflow now enforces dashboard ownership for Publishers, renders submitted and published articles read-only to their authors, and exposes explicit Admin/Superadmin Publish, Return to draft, and Unpublish actions. The list has a role-scoped status filter. Save requests are guarded against duplicate in-flight actions, and duplicate-slug errors during block replacement roll back the complete article update rather than escaping as a server error.

The article editor now uploads or reuses images permitted by the existing role-scoped media API, inserts them as ordered body blocks, lets draft authors add, move, and remove sections, and previews private files through authenticated blob requests with revocable object URLs. Announcement and page editors use the same ordered block workflow, with expiry and Admin-only page management. Public articles, announcements, and pages render the resolved picture blocks in order using the same safe text-and-picture sequence.
