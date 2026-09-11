# Milestone 6 Content Media Backend

## Status: implemented

Publishers can upload and list their own images. Admins and Superadmins retain full media-library access, including updates, deletion, and external-link creation.

Content endpoints reject a Publisher’s attempt to attach another user’s image by guessed ID, for both featured and inline pictures. Existing image attachments remain valid when a Publisher updates their draft.

Uploaded image files now check authorization on every request. The uploader and Admins may retrieve them while private. Anonymous visitors may retrieve an image only while it is referenced by published article, announcement, or page content; an expired announcement does not grant access. Unpublishing removes public access on the next request. Responses use `Cache-Control: no-store` and `X-Content-Type-Options: nosniff`.

The next stage adds dashboard services and editors, authenticated image previews, and public picture rendering.
