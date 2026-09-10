from functools import wraps

from flask import jsonify
from flask_jwt_extended import get_current_user, jwt_required

from backend.extensions import db, jwt
from backend.models import User, UserRole


ROLE_LEVELS = {
    UserRole.VISITOR: 0,
    UserRole.PUBLISHER: 10,
    UserRole.ADMIN: 20,
    UserRole.SUPERADMIN: 30,
}


def _authentication_error():
    return jsonify(error="Authentication required"), 401


@jwt.unauthorized_loader
def _missing_token(_reason):
    return _authentication_error()


@jwt.invalid_token_loader
def _invalid_token(_reason):
    return _authentication_error()


@jwt.expired_token_loader
def _expired_token(_header, _payload):
    return _authentication_error()


@jwt.revoked_token_loader
def _revoked_token(_header, _payload):
    return _authentication_error()


@jwt.user_lookup_error_loader
def _unknown_user(_header, _payload):
    return _authentication_error()


@jwt.user_lookup_loader
def load_authenticated_user(_header, jwt_data):
    identity = jwt_data.get("sub")
    if not isinstance(identity, str):
        return None
    try:
        user_id = int(identity)
    except ValueError:
        return None
    if user_id <= 0:
        return None
    user = db.session.get(User, user_id)
    if (
        user is not None
        and user.role is UserRole.SUPERADMIN
        and jwt_data.get("auth_channel") != "superadmin"
    ):
        return None
    return user


def login_required(view):
    @wraps(view)
    @jwt_required()
    def wrapped(*args, **kwargs):
        if get_current_user() is None:
            return _authentication_error()
        return view(*args, **kwargs)

    return wrapped


def role_required(min_role):
    try:
        required_role = UserRole(min_role)
    except ValueError as error:
        raise ValueError(f"Unknown role: {min_role}") from error

    def decorator(view):
        @wraps(view)
        @login_required
        def wrapped(*args, **kwargs):
            user = get_current_user()
            if ROLE_LEVELS[user.role] < ROLE_LEVELS[required_role]:
                return jsonify(error="Insufficient permissions"), 403
            return view(*args, **kwargs)

        return wrapped

    return decorator
