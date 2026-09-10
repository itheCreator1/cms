import logging

from flask import Blueprint, current_app, jsonify, request, send_from_directory
from flask_jwt_extended import get_current_user
from sqlalchemy.exc import IntegrityError

from backend.extensions import db
from backend.models import Media
from backend.services.media_storage import InvalidMedia, MediaTooLarge
from backend.utils.auth_helpers import role_required
from backend.utils.media import (
    normalize_alt_text,
    normalize_external_url,
    serialize_media,
)


blueprint = Blueprint("media", __name__, url_prefix="/api/media")
logger = logging.getLogger("cms.media")


def _invalid():
    return jsonify(error="Invalid media data"), 400


@blueprint.get("")
@role_required("admin")
def list_media():
    items = db.session.scalars(db.select(Media).order_by(Media.id)).all()
    return jsonify(items=[serialize_media(item) for item in items])


@blueprint.get("/<int:media_id>")
@role_required("admin")
def get_media(media_id):
    item = db.session.get(Media, media_id)
    if item is None:
        return jsonify(error="Not found"), 404
    return jsonify(item=serialize_media(item))


@blueprint.post("/uploads")
@role_required("admin")
def create_upload():
    uploaded_file = request.files.get("file")
    if uploaded_file is None:
        return _invalid()
    try:
        alt_text = normalize_alt_text(request.form.get("alt_text"))
        stored = current_app.extensions["media_storage"].save_image(
            uploaded_file,
            current_app.config["MEDIA_MAX_BYTES"],
            current_app.config["MEDIA_MAX_PIXELS"],
        )
    except MediaTooLarge:
        return jsonify(error="Upload too large"), 413
    except InvalidMedia:
        return _invalid()

    item = Media(
        filename=stored.filename,
        url=f"/api/media/files/{stored.storage_key}",
        uploaded_by=get_current_user().id,
        file_type=stored.file_type,
        source_type="upload",
        media_type="image",
        provider="local",
        storage_key=stored.storage_key,
        alt_text=alt_text,
    )
    db.session.add(item)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        current_app.extensions["media_storage"].delete(stored.storage_key)
        return jsonify(error="Media URL is already in use"), 409
    return jsonify(item=serialize_media(item)), 201


@blueprint.post("/links")
@role_required("admin")
def create_link():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return _invalid()
    try:
        url, host, provider, media_type = normalize_external_url(payload.get("url"))
        alt_text = normalize_alt_text(payload.get("alt_text"))
    except ValueError:
        return _invalid()
    item = Media(
        filename=host,
        url=url,
        uploaded_by=get_current_user().id,
        file_type="text/uri-list",
        source_type="external",
        media_type=media_type,
        provider=provider,
        alt_text=alt_text,
    )
    db.session.add(item)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify(error="Media URL is already in use"), 409
    return jsonify(item=serialize_media(item)), 201


@blueprint.put("/<int:media_id>")
@role_required("admin")
def update_media(media_id):
    item = db.session.get(Media, media_id)
    if item is None:
        return jsonify(error="Not found"), 404
    payload = request.get_json(silent=True)
    allowed = {"alt_text"} if item.source_type == "upload" else {"alt_text", "url"}
    if not isinstance(payload, dict) or not payload or not set(payload) <= allowed:
        return _invalid()
    try:
        if "alt_text" in payload:
            item.alt_text = normalize_alt_text(payload["alt_text"])
        if "url" in payload:
            url, host, provider, media_type = normalize_external_url(payload["url"])
            item.url = url
            item.filename = host
            item.provider = provider
            item.media_type = media_type
    except ValueError:
        return _invalid()
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify(error="Media URL is already in use"), 409
    return jsonify(item=serialize_media(item))


@blueprint.delete("/<int:media_id>")
@role_required("admin")
def delete_media(media_id):
    item = db.session.get(Media, media_id)
    if item is None:
        return jsonify(error="Not found"), 404
    storage_key = item.storage_key
    db.session.delete(item)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify(error="Resource is in use"), 409
    try:
        current_app.extensions["media_storage"].delete(storage_key)
    except OSError:
        logger.exception("Failed to remove an orphaned local media file")
    return "", 204


@blueprint.get("/files/<storage_key>")
def serve_media(storage_key):
    if not storage_key or "/" in storage_key or "\\" in storage_key:
        return jsonify(error="Not found"), 404
    response = send_from_directory(
        current_app.config["MEDIA_STORAGE_ROOT"], storage_key, conditional=True
    )
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response
