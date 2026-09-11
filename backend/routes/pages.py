from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_current_user
from sqlalchemy.exc import IntegrityError

from backend.extensions import db
from backend.models import Page, PageBodyBlock, PageStatus
from backend.utils.auth_helpers import role_required
from backend.utils.body_blocks import parse_body_input, replace_blocks, serialize_blocks
from backend.utils.content import iso, is_admin, optional_user, valid_slug, valid_text

blueprint = Blueprint("pages", __name__, url_prefix="/api/pages")


def _serialize(item):
    return {
        "id": item.id,
        "title": item.title,
        "slug": item.slug,
        "body": item.body,
        "body_blocks": serialize_blocks(item),
        "status": item.status.value,
        "author_id": item.author_id,
        "updated_at": iso(item.updated_at),
    }


def _visible(user):
    statement = db.select(Page).order_by(Page.id)
    return statement if is_admin(user) else statement.where(Page.status == PageStatus.PUBLISHED)


@blueprint.get("")
def list_pages():
    user = optional_user()
    return jsonify(items=[_serialize(item) for item in db.session.scalars(_visible(user)).all()])


@blueprint.get("/<int:item_id>")
def get_page(item_id):
    user = optional_user()
    item = db.session.execute(
        _visible(user).where(Page.id == item_id)
    ).scalar_one_or_none()
    if item is None:
        return jsonify(error="Not found"), 404
    return jsonify(item=_serialize(item))


@blueprint.get("/slug/<slug>")
def get_page_by_slug(slug):
    user = optional_user()
    item = db.session.execute(
        _visible(user).where(Page.slug == slug)
    ).scalar_one_or_none()
    if item is None:
        return jsonify(error="Not found"), 404
    return jsonify(item=_serialize(item))


def _payload(payload, partial=False):
    if not isinstance(payload, dict):
        raise ValueError
    changes = {}
    for name, maximum in (("title", 255), ("slug", 255)):
        if name not in payload:
            if not partial:
                raise ValueError
            continue
        value = payload[name]
        if (name == "slug" and not valid_slug(value, maximum)) or (
            name != "slug" and not valid_text(value, maximum)
        ):
            raise ValueError
        changes[name] = value.strip()
    return changes


@blueprint.post("")
@role_required("admin")
def create_page():
    payload = request.get_json(silent=True)
    try:
        body, blocks = parse_body_input(payload)
        changes = _payload(payload)
        status = PageStatus(payload.get("status", "draft"))
    except (ValueError, TypeError):
        return jsonify(error="Invalid content data"), 400
    item = Page(**changes, body=body, status=status, author_id=get_current_user().id)
    replace_blocks(item, blocks, PageBodyBlock)
    db.session.add(item)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify(error="Slug is already in use"), 409
    return jsonify(item=_serialize(item)), 201


@blueprint.put("/<int:item_id>")
@role_required("admin")
def update_page(item_id):
    item = db.session.get(Page, item_id)
    if item is None:
        return jsonify(error="Not found"), 404
    payload = request.get_json(silent=True)
    try:
        body, blocks = parse_body_input(payload, partial=True)
        changes = _payload(payload, partial=True)
        status = PageStatus(payload.get("status", item.status.value))
    except (ValueError, TypeError, AttributeError):
        return jsonify(error="Invalid content data"), 400
    if body is not None:
        changes["body"] = body
    for name, value in changes.items():
        setattr(item, name, value)
    if blocks is not None:
        replace_blocks(item, blocks, PageBodyBlock)
    item.status = status
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify(error="Slug is already in use"), 409
    return jsonify(item=_serialize(item))


@blueprint.delete("/<int:item_id>")
@role_required("admin")
def delete_page(item_id):
    item = db.session.get(Page, item_id)
    if item is None:
        return jsonify(error="Not found"), 404
    db.session.delete(item)
    db.session.commit()
    return "", 204
