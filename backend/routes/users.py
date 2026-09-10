from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_current_user
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from backend.extensions import db
from backend.models import User, UserRole
from backend.utils.auth_helpers import role_required
from backend.utils.users import new_user_values, serialize_public_user, user_changes


blueprint = Blueprint("users", __name__, url_prefix="/api/users")


def _is_superadmin(user):
    return user.role is UserRole.SUPERADMIN


def _can_manage(actor, target):
    return _is_superadmin(actor) or target.role is UserRole.PUBLISHER


def _protected_superadmin(actor, target, next_role=None):
    if target.id == actor.id and (
        next_role is None or next_role is not UserRole.SUPERADMIN
    ):
        return True
    if target.role is not UserRole.SUPERADMIN:
        return False
    if next_role is UserRole.SUPERADMIN:
        return False
    count = db.session.scalar(
        db.select(func.count()).select_from(User).where(User.role == UserRole.SUPERADMIN)
    )
    return count <= 1


@blueprint.get("")
@role_required("admin")
def list_users():
    actor = get_current_user()
    statement = db.select(User).order_by(User.id)
    if not _is_superadmin(actor):
        statement = statement.where(User.role == UserRole.PUBLISHER)
    return jsonify(
        items=[serialize_public_user(user) for user in db.session.scalars(statement)]
    )


@blueprint.get("/<int:user_id>")
@role_required("admin")
def get_user(user_id):
    target = db.session.get(User, user_id)
    if target is None:
        return jsonify(error="Not found"), 404
    if not _can_manage(get_current_user(), target):
        return jsonify(error="Insufficient permissions"), 403
    return jsonify(item=serialize_public_user(target))


@blueprint.post("")
@role_required("admin")
def create_user():
    try:
        email, password, role = new_user_values(request.get_json(silent=True))
    except ValueError:
        return jsonify(error="Invalid user data"), 400
    if not _is_superadmin(get_current_user()) and role is not UserRole.PUBLISHER:
        return jsonify(error="Insufficient permissions"), 403
    user = User(email=email, role=role)
    user.set_password(password)
    db.session.add(user)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify(error="Email is already registered"), 409
    return jsonify(item=serialize_public_user(user)), 201


@blueprint.put("/<int:user_id>")
@role_required("admin")
def update_user(user_id):
    target = db.session.get(User, user_id)
    if target is None:
        return jsonify(error="Not found"), 404
    actor = get_current_user()
    if not _can_manage(actor, target):
        return jsonify(error="Insufficient permissions"), 403
    try:
        changes = user_changes(request.get_json(silent=True))
    except ValueError:
        return jsonify(error="Invalid user data"), 400
    next_role = changes.get("role", target.role)
    if not _is_superadmin(actor) and next_role is not UserRole.PUBLISHER:
        return jsonify(error="Insufficient permissions"), 403
    if _protected_superadmin(actor, target, next_role):
        return jsonify(error="Active Superadmin account is protected"), 409

    if "email" in changes:
        target.email = changes["email"]
    if "password" in changes:
        target.set_password(changes["password"])
    target.role = next_role
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify(error="Email is already registered"), 409
    return jsonify(item=serialize_public_user(target))


@blueprint.delete("/<int:user_id>")
@role_required("admin")
def delete_user(user_id):
    target = db.session.get(User, user_id)
    if target is None:
        return jsonify(error="Not found"), 404
    actor = get_current_user()
    if not _can_manage(actor, target):
        return jsonify(error="Insufficient permissions"), 403
    if _protected_superadmin(actor, target):
        return jsonify(error="Active Superadmin account is protected"), 409
    db.session.delete(target)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify(error="User is in use"), 409
    return "", 204
