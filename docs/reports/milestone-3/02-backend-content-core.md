# Milestone 3 Backend Content Core

## Status: complete

The backend now exposes REST JSON APIs for articles, announcements, and pages. Anonymous and authenticated Visitor reads are limited to published content; expired announcements are excluded. Publishers can see their own content alongside public content, manage only their own drafts, and submit articles and announcements for review. Admins and Superadmins can manage all content and control publication. Pages require Admin or Superadmin access.

Article validation covers required text, safe slugs, categories, tags, featured media, status values, and duplicate slugs. Announcement validation includes timezone-aware expiration values. Responses use consistent item, collection, and sanitized error objects.

The `announcement_status` PostgreSQL enum now includes `pending_review`. Revision `5e2d9a6b1c44` upgrades the type and has a reviewed downgrade that maps submitted announcements back to draft before rebuilding the original enum.

## Verification evidence

```text
docker compose run --rm backend pytest backend/tests/test_content_api.py -q
10 passed

docker compose run --rm backend pytest backend/tests -q
99 passed in 13.73s
```

The full suite includes PostgreSQL migration upgrade/downgrade, model metadata, authentication, seed behavior, content CRUD, ownership, role boundaries, public visibility, relationship validation, and JSON error coverage.
