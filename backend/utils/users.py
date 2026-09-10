from backend.models import UserRole
from backend.utils.validation import normalize_email


def serialize_public_user(user):
    return {
        "id": user.id,
        "email": user.email,
        "role": user.role.value,
        "created_at": user.created_at.isoformat(),
    }


def new_user_values(payload):
    if not isinstance(payload, dict):
        raise ValueError
    email = normalize_email(payload.get("email"))
    password = payload.get("password")
    try:
        role = UserRole(payload.get("role"))
    except (TypeError, ValueError):
        raise ValueError from None
    if email is None or not isinstance(password, str) or not 12 <= len(password) <= 128:
        raise ValueError
    return email, password, role


def user_changes(payload):
    if (
        not isinstance(payload, dict)
        or not payload
        or not set(payload) <= {"email", "password", "role"}
    ):
        raise ValueError
    changes = {}
    if "email" in payload:
        email = normalize_email(payload["email"])
        if email is None:
            raise ValueError
        changes["email"] = email
    if "password" in payload:
        password = payload["password"]
        if not isinstance(password, str) or not 12 <= len(password) <= 128:
            raise ValueError
        changes["password"] = password
    if "role" in payload:
        try:
            changes["role"] = UserRole(payload["role"])
        except (TypeError, ValueError):
            raise ValueError from None
    return changes
