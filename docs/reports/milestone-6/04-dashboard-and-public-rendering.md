# Milestone 6 Dashboard and Public Rendering

## Status: in progress

Article-save correction: the editor sends explicit writable fields and one body representation, strips resolved image metadata from requests, preserves block order and publication status, and exposes load failures with retry. Existing text blocks can be edited individually without removing picture references. Repeated backend block replacement flushes removed rows inside the transaction before reusing their positions.

Verification for this correction: 127 backend tests, 45 frontend tests, and the frontend production build passed in Compose. Regression coverage includes repeated block replacement/reordering/removal, published article metadata saves retaining pictures, and editor load failures. Authenticated Playwright acceptance remains pending.

The first dashboard slice replaces the placeholder with authenticated article management routes. Publishers can list their own articles, create a draft, edit a draft, and submit it for review. The dashboard retains loading, error, empty, and retry states, and unknown dashboard URLs remain behind the authentication boundary.

The next additions to this stage are shared picture-block editing and previews, announcement and page workflows, role-specific publication controls, media upload/picking, and public picture-block rendering.
