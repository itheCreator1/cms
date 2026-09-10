import re

from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, get_current_user
from sqlalchemy.exc import IntegrityError

from backend.extensions import db, limiter
from backend.models import User, UserRole
from backend.utils.auth_helpers import login_required
from backend.utils.security_logging import log_superadmin_attempt

blueprint = Blueprint("auth", __name__, url_prefix="/api")

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _signup_credentials():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return None
    email = data.get("email")
    password = data.get("password")
    if not isinstance(email, str) or not isinstance(password, str):
        return None
    email = email.strip().casefold()
    if not EMAIL_PATTERN.fullmatch(email) or not 12 <= len(password) <= 128:
        return None
    return email, password


def _login_credentials():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return None
    email = data.get("email")
    password = data.get("password")
    if not isinstance(email, str) or not isinstance(password, str):
        return None
    email = email.strip().casefold()
    if not EMAIL_PATTERN.fullmatch(email) or not password or len(password) > 128:
        return None
    return email, password


def _public_user(user):
    return {
        "id": user.id,
        "email": user.email,
        "role": user.role.value,
        "created_at": user.created_at.isoformat(),
    }


def _successful_login(user):
    token = create_access_token(
        identity=str(user.id),
        additional_claims={"role": user.role.value},
    )
    return jsonify(access_token=token, user=_public_user(user))


def _invalid_credentials():
    return jsonify(error="Invalid credentials"), 401


@blueprint.post("/signup")
def signup():
    credentials = _signup_credentials()
    if credentials is None:
        return jsonify(error="Invalid signup data"), 400

    email, password = credentials
    if db.session.execute(db.select(User).where(User.email == email)).scalar_one_or_none():
        return jsonify(error="Email is already registered"), 409

    user = User(email=email)
    user.set_password(password)
    db.session.add(user)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify(error="Email is already registered"), 409

    return jsonify(user=_public_user(user)), 201


@blueprint.post("/login")
@limiter.limit("20 per minute")
def login():
    credentials = _login_credentials()
    if credentials is None:
        return jsonify(error="Invalid login data"), 400

    email, password = credentials
    user = db.session.execute(
        db.select(User).where(User.email == email)
    ).scalar_one_or_none()
    password_matches = user is not None and user.check_password(password)
    permitted_roles = {UserRole.VISITOR, UserRole.PUBLISHER, UserRole.ADMIN}
    if not password_matches or user.role not in permitted_roles:
        return _invalid_credentials()
    return _successful_login(user)


def _superadmin_limit_breached(_request_limit):
    log_superadmin_attempt(request.remote_addr, "failure")


@blueprint.post("/superadmin-login")
@limiter.limit("5 per minute", on_breach=_superadmin_limit_breached)
def superadmin_login():
    credentials = _login_credentials()
    if credentials is None:
        log_superadmin_attempt(request.remote_addr, "failure")
        return jsonify(error="Invalid login data"), 400

    email, password = credentials
    user = db.session.execute(
        db.select(User).where(User.email == email)
    ).scalar_one_or_none()
    # Every found account has its password verified before its role is considered.
    password_matches = user is not None and user.check_password(password)
    if not password_matches or user.role is not UserRole.SUPERADMIN:
        log_superadmin_attempt(request.remote_addr, "failure")
        return _invalid_credentials()

    response = _successful_login(user)
    log_superadmin_attempt(request.remote_addr, "success")
    return response


@blueprint.get("/me")
@login_required
def me():
    return jsonify(user=_public_user(get_current_user()))
