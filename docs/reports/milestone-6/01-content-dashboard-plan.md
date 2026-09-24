# Milestone 6: Content Dashboard and Publisher Pictures

## Summary

Build a working dashboard for writing, reviewing, and publishing articles, announcements, and static pages.

Documentation and recent commits establish milestones 1–5 as complete. This milestone depends on the reusable frontend foundation, then replaces the dashboard placeholder and adds the requested ability for publishers to upload pictures into their posts.

## Reusable frontend foundation dependency

Complete the reusable frontend foundation before dashboard services and screens. It is a prerequisite, not a replacement for this milestone's dashboard or publisher-picture requirements.

- Use `src/layouts/PublicLayout.jsx`, `AuthLayout.jsx`, and `DashboardLayout.jsx` for their respective route areas. Each layout owns its outer structure; route pages compose content inside it.
- Use `src/components/layout/Header.jsx`, `Navigation.jsx`, and `Footer.jsx` for shared site chrome. Navigation changes belong in `Navigation.jsx`; global header and footer changes belong in their named components.
- Use `src/components/ui/Button.jsx` and `FormField.jsx` for shared control behavior and states. Keep generic controls focused and put feature-specific presentation in their consuming components.
- Keep the homepage's presentational sections in `src/components/home/HomeIntro.jsx`, `AnnouncementSection.jsx`, and `ArticleSection.jsx`. `src/hooks/useHomeContent.js` coordinates homepage loading, and `src/pages/public/Home.jsx` is the single edit point for homepage section order.
- Keep the global reset and theme tokens in `src/styles.css`. Move layout, page, and component rules to co-located CSS Modules that consume those tokens, so theme changes originate from one token source.
- Preserve React Router, the shared API client, existing public-content behavior, and role-aware protected routes while applying the foundation.

## Dashboard and editing

- Add content lists and new/edit routes under `/dashboard/articles`, `/dashboard/announcements`, and `/dashboard/pages`.
- Publishers see their own articles and announcements. Admins and Superadmins see all content; page management requires Admin access.
- Provide status filters, loading/empty/error states, retry controls, and deletion confirmation.
- Use simple text sections with an “Add picture” button between sections. Support moving and removing sections and previewing the result. No Markdown or rich-text formatting.
- Articles include title, editable slug, category, tags, and an optional main picture. Announcements include optional expiry; pages include title and slug.
- Publishers save drafts and submit saved drafts for review. Submitted and published posts are read-only to their publisher.
- Admins can edit, publish, unpublish, or return content to draft. Saving edits preserves the current status unless a status action is explicitly selected.
- Preserve form input after failed saves, prevent duplicate submissions, and warn before leaving unsaved changes. Expired sessions require login again without silently discarding the open editor.

## Pictures, permissions, and storage

- Allow Publisher-level access to image uploads. Publishers browse and reuse only their own uploaded pictures; admins browse all pictures.
- Apply ownership checks on the backend when attaching main or inline pictures. Publishers may retain an existing picture assigned by an admin but cannot attach another user’s picture by guessing its ID.
- Keep existing decoded-image validation, generated storage names, metadata removal, and storage adapter. Accept the existing JPEG, PNG, WebP, and non-animated GIF formats and configured limits.
- Removing a picture from a post detaches it; it does not delete the uploaded file. Global media editing and deletion remain admin-only.
- Make uploaded files accessible only to their uploader and admins unless referenced by published content. Expired announcements do not grant public access.
- Recheck visibility on every image request, including after unpublishing. Use `Cache-Control: no-store`; previously downloaded copies cannot be recalled.
- Dashboard previews fetch private images with bearer authentication and render temporary object URLs, revoking them when no longer needed. Never put tokens in image URLs.

## API, schema, and public rendering

- Extend existing content requests and responses with ordered `body_blocks`: text blocks contain `text`; image blocks contain `media_id`. Responses include resolved image metadata for rendering.
- Store blocks in separate ordered child tables for articles, announcements, and pages, with real content and media foreign keys. Content deletion removes its blocks; referenced media deletion returns `409`.
- Generate and review an Alembic migration that backfills every existing body as a text block. Preserve the existing `body` field as a plain-text projection for excerpts and compatibility.
- Existing body-only clients remain supported: a body update replaces the block sequence with text. Requests supplying both representations are rejected; updates supplying neither preserve the body.
- Validate block types, nonempty text content, uploaded-image references, and attachment permissions. Save block replacements and content changes atomically.
- Extend the shared API client to support multipart uploads and authenticated image responses while preserving anonymous public requests.
- Render the same safe text-and-picture sequence in previews, public articles, full announcements, and pages. Homepage summaries remain compact.
- Keep Flask Blueprints, centralized numeric authorization, React Router, and focused service/component boundaries.

## Verification and delivery

Implement in focused stages: documentation; reusable frontend foundation; models and migration; backend content/media behavior; dashboard services and screens; public rendering; final verification. Write failing behavior tests before implementation and keep tests and implementation commits focused.

Required coverage:

- Publisher ownership, admin access, direct-route restrictions, and draft/review/publish transitions.
- Upload validation, cross-user attachment rejection, private image access, publication, unpublishing, expiry, and shared-image references.
- Block ordering, removal, safe text rendering, failed saves, upload retries, and multipart headers.
- Existing content migration, plain-text API compatibility, and foreign-key protection.
- Browser smoke journey: publisher uploads pictures and submits a post; admin publishes it; visitor sees it; unpublishing removes public content and image access.

Run both complete test suites and the frontend production build inside Compose, verify service health, and confirm migration head alignment.

Update `spec.md` with the agreed publisher-media permissions, plus README, TODO, and milestone reports. Preserve the existing deleted audit and untracked `.diagram-design`.

Taxonomy administration, full media management, user administration, Superadmin-authorized site-wide settings, and comprehensive automated end-to-end coverage remain subsequent milestones. Site-wide settings require persistent, validated backend configuration and a dashboard management experience; add and retain that work in the tracker.
