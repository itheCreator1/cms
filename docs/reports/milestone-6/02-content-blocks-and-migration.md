# Milestone 6 Content Blocks and Migration

## Status: implemented

Articles, announcements, and pages now store ordered text and image blocks in dedicated child tables. Each API response includes `body_blocks`; image blocks include the referenced media metadata needed by the dashboard and public renderer.

The existing `body` field remains a plain-text projection of text blocks, preserving current excerpt and body-only client behavior. A body-only create or update converts the supplied value to a single text block. Requests that send both `body` and `body_blocks` are rejected as ambiguous, while partial updates that supply neither leave the content unchanged.

The reviewed `a6c8d9e1f2b3` Alembic revision creates the three block tables and backfills every existing content body as its first text block. Blocks are cascade-deleted with their content. Media references use restrictive foreign keys so referenced files cannot be deleted.

Publisher image ownership and private-file delivery are the next Milestone 6 stage. The current block validation accepts only uploaded image media; ownership validation will be added with that media authorization work.
