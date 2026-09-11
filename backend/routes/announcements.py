from datetime import datetime, timezone

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_current_user
from sqlalchemy import and_, or_

from backend.extensions import db
from backend.models import Announcement, AnnouncementBodyBlock, AnnouncementStatus, UserRole
from backend.utils.auth_helpers import role_required
from backend.utils.body_blocks import parse_body_input, replace_blocks, serialize_blocks
from backend.utils.content import (
    can_manage_draft,
    iso,
    is_admin,
    optional_user,
    parse_datetime,
    published_at_for,
    valid_text,
)

blueprint = Blueprint("announcements", __name__, url_prefix="/api/announcements")


def _serialize(item):
    return {
        "id": item.id,
        "title": item.title,
        "body": item.body,
        "body_blocks": serialize_blocks(item),
        "status": item.status.value,
        "author_id": item.author_id,
        "created_at": iso(item.created_at),
        "published_at": iso(item.published_at),
        "expires_at": iso(item.expires_at),
    }


def _visible(user):
    statement = db.select(Announcement).order_by(Announcement.id)
    if is_admin(user):
        return statement
    now = datetime.now(timezone.utc)
    published = and_(
        Announcement.status == AnnouncementStatus.PUBLISHED,
        or_(Announcement.expires_at.is_(None), Announcement.expires_at > now),
    )
    if user is not None and user.role is UserRole.PUBLISHER:
        return statement.where(or_(published, Announcement.author_id == user.id))
    return statement.where(published)


@blueprint.get("")
def list_announcements():
    user = optional_user()
    return jsonify(
        items=[_serialize(item) for item in db.session.scalars(_visible(user)).all()]
    )


@blueprint.get("/<int:item_id>")
def get_announcement(item_id):
    user = optional_user()
    item = db.session.execute(
        _visible(user).where(Announcement.id == item_id)
    ).scalar_one_or_none()
    if item is None:
        return jsonify(error="Not found"), 404
    return jsonify(item=_serialize(item))


def _payload(payload, partial=False):
    if not isinstance(payload, dict):
        raise ValueError
    changes = {}
    for name, maximum in (("title", 255),):
        if name not in payload:
            if not partial:
                raise ValueError
            continue
        if not valid_text(payload[name], maximum):
            raise ValueError
        changes[name] = payload[name].strip()
    if "expires_at" in payload:
        changes["expires_at"] = parse_datetime(payload["expires_at"])
    return changes


@blueprint.post("")
@role_required("publisher")
def create_announcement():
    user = get_current_user()
    payload = request.get_json(silent=True)
    if not is_admin(user) and isinstance(payload, dict) and payload.get("status", "draft") != "draft":
        return jsonify(error="Insufficient permissions"), 403
    try:
        body, blocks = parse_body_input(payload)
        changes = _payload(payload)
        status = AnnouncementStatus(payload.get("status", "draft")) if is_admin(user) else AnnouncementStatus.DRAFT
    except (ValueError, TypeError):
        return jsonify(error="Invalid content data"), 400
    item = Announcement(
        **changes, body=body,
        author_id=user.id,
        status=status,
        published_at=published_at_for(status),
    )
    replace_blocks(item, blocks, AnnouncementBodyBlock)
    db.session.add(item)
    db.session.commit()
    return jsonify(item=_serialize(item)), 201


@blueprint.put("/<int:item_id>")
@role_required("publisher")
def update_announcement(item_id):
    item = db.session.get(Announcement, item_id)
    if item is None:
        return jsonify(error="Not found"), 404
    user = get_current_user()
    if not can_manage_draft(user, item):
        return jsonify(error="Insufficient permissions"), 403
    payload = request.get_json(silent=True)
    try:
        body, blocks = parse_body_input(payload, partial=True)
        changes = _payload(payload, partial=True)
        status = AnnouncementStatus(payload.get("status", item.status.value))
    except (ValueError, TypeError, AttributeError):
        return jsonify(error="Invalid content data"), 400
    if not is_admin(user) and status not in {
        AnnouncementStatus.DRAFT,
        AnnouncementStatus.PENDING_REVIEW,
    }:
        return jsonify(error="Insufficient permissions"), 403
    if body is not None:
        changes["body"] = body
    for name, value in changes.items():
        setattr(item, name, value)
    if blocks is not None:
        replace_blocks(item, blocks, AnnouncementBodyBlock)
    item.status = status
    item.published_at = published_at_for(status, item.published_at)
    db.session.commit()
    return jsonify(item=_serialize(item))


@blueprint.delete("/<int:item_id>")
@role_required("publisher")
def delete_announcement(item_id):
    item = db.session.get(Announcement, item_id)
    if item is None:
        return jsonify(error="Not found"), 404
    if not can_manage_draft(get_current_user(), item):
        return jsonify(error="Insufficient permissions"), 403
    db.session.delete(item)
    db.session.commit()
    return "", 204
