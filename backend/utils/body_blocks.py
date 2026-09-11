from backend.extensions import db
from backend.models import Media
from backend.utils.content import valid_text
from backend.utils.media import serialize_media


def parse_body_input(payload, partial=False, may_attach_media=None):
    has_body = "body" in payload
    has_blocks = "body_blocks" in payload
    if has_body and has_blocks:
        raise ValueError
    if not has_body and not has_blocks:
        if partial:
            return None, None
        raise ValueError
    if has_body:
        if not valid_text(payload["body"]):
            raise ValueError
        text = payload["body"].strip()
        return text, [("text", text)]
    blocks = payload["body_blocks"]
    if not isinstance(blocks, list) or not blocks:
        raise ValueError
    normalized, text_parts = [], []
    for block in blocks:
        if not isinstance(block, dict) or set(block) - {"type", "text", "media_id"}:
            raise ValueError
        if block.get("type") == "text" and set(block) == {"type", "text"} and valid_text(block["text"]):
            text = block["text"].strip()
            normalized.append(("text", text))
            text_parts.append(text)
        elif block.get("type") == "image" and set(block) == {"type", "media_id"}:
            media_id = block["media_id"]
            media = db.session.get(Media, media_id) if isinstance(media_id, int) and not isinstance(media_id, bool) else None
            if (
                media is None
                or media.source_type != "upload"
                or media.media_type != "image"
                or (may_attach_media is not None and not may_attach_media(media))
            ):
                raise ValueError
            normalized.append(("image", media))
        else:
            raise ValueError
    if not text_parts:
        raise ValueError
    return "\n\n".join(text_parts), normalized


def replace_blocks(item, blocks, block_model):
    if item.id is not None:
        item.body_blocks.clear()
        # Release unique positions before inserting replacements, without committing.
        db.session.flush()
    item.body_blocks[:] = [
        block_model(position=position, text=value if kind == "text" else None, media=value if kind == "image" else None)
        for position, (kind, value) in enumerate(blocks)
    ]


def serialize_blocks(item):
    return [
        {"type": "text", "text": block.text}
        if block.text is not None
        else {"type": "image", "media_id": block.media_id, "media": serialize_media(block.media)}
        for block in item.body_blocks
    ]
