from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_current_user

from backend.extensions import db
from backend.models.settings import SiteSettings, SiteSettingsChange
from backend.utils.auth_helpers import role_required


blueprint = Blueprint("settings", __name__, url_prefix="/api/settings")
FIELDS = {"site_name": 120, "tagline": 160, "homepage_headline": 180, "homepage_intro": 2000}


def _serialize(settings):
    return {field: getattr(settings, field) for field in FIELDS}


@blueprint.get("")
def get_settings():
    return jsonify(item=_serialize(db.session.get(SiteSettings, 1)))


@blueprint.put("")
@role_required("superadmin")
def update_settings():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict) or not payload or not set(payload) <= set(FIELDS):
        return jsonify(error="Invalid settings data"), 400
    changes = {}
    for field, limit in FIELDS.items():
        if field not in payload:
            continue
        value = payload[field]
        if not isinstance(value, str):
            return jsonify(error="Invalid settings data"), 400
        value = value.strip()
        if not value or len(value) > limit or any(ord(char) < 32 and char not in "\n\r\t" for char in value):
            return jsonify(error="Invalid settings data"), 400
        changes[field] = value
    settings = db.session.get(SiteSettings, 1)
    before = _serialize(settings)
    for field, value in changes.items():
        setattr(settings, field, value)
    after = _serialize(settings)
    if before != after:
        db.session.add(SiteSettingsChange(actor_id=get_current_user().id, before_values=before, after_values=after))
        db.session.commit()
    return jsonify(item=after)
