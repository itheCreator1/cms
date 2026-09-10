from backend.utils.content import valid_slug, valid_text


def serialize_taxonomy(item):
    return {"id": item.id, "name": item.name, "slug": item.slug}


def taxonomy_changes(payload, partial=False):
    if not isinstance(payload, dict) or (partial and not payload):
        raise ValueError

    changes = {}
    for field in ("name", "slug"):
        if field not in payload:
            if not partial:
                raise ValueError
            continue
        value = payload[field]
        valid = valid_text(value, 100) if field == "name" else valid_slug(value, 100)
        if not valid:
            raise ValueError
        changes[field] = value.strip()

    if not changes:
        raise ValueError
    return changes
