from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError

from backend.extensions import db
from backend.models import Category
from backend.utils.auth_helpers import role_required
from backend.utils.taxonomy import serialize_taxonomy, taxonomy_changes


blueprint = Blueprint("categories", __name__, url_prefix="/api/categories")


@blueprint.get("")
def list_categories():
    items = db.session.scalars(db.select(Category).order_by(Category.id)).all()
    return jsonify(items=[serialize_taxonomy(item) for item in items])


@blueprint.get("/<int:category_id>")
def get_category(category_id):
    item = db.session.get(Category, category_id)
    if item is None:
        return jsonify(error="Not found"), 404
    return jsonify(item=serialize_taxonomy(item))


@blueprint.post("")
@role_required("admin")
def create_category():
    try:
        item = Category(**taxonomy_changes(request.get_json(silent=True)))
    except ValueError:
        return jsonify(error="Invalid taxonomy data"), 400
    db.session.add(item)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify(error="Name or slug is already in use"), 409
    return jsonify(item=serialize_taxonomy(item)), 201


@blueprint.put("/<int:category_id>")
@role_required("admin")
def update_category(category_id):
    item = db.session.get(Category, category_id)
    if item is None:
        return jsonify(error="Not found"), 404
    try:
        changes = taxonomy_changes(request.get_json(silent=True), partial=True)
    except ValueError:
        return jsonify(error="Invalid taxonomy data"), 400
    for field, value in changes.items():
        setattr(item, field, value)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify(error="Name or slug is already in use"), 409
    return jsonify(item=serialize_taxonomy(item))


@blueprint.delete("/<int:category_id>")
@role_required("admin")
def delete_category(category_id):
    item = db.session.get(Category, category_id)
    if item is None:
        return jsonify(error="Not found"), 404
    db.session.delete(item)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify(error="Resource is in use"), 409
    return "", 204
