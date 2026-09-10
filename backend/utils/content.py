import re
from datetime import datetime, timezone

from flask_jwt_extended import get_current_user, verify_jwt_in_request

from backend.models import UserRole
from backend.utils.auth_helpers import ROLE_LEVELS


SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def optional_user():
    verify_jwt_in_request(optional=True)
    return get_current_user()


def is_admin(user):
    return user is not None and ROLE_LEVELS[user.role] >= ROLE_LEVELS[UserRole.ADMIN]


def can_manage_draft(user, item):
    if is_admin(user):
        return True
    return (
        user is not None
        and user.role is UserRole.PUBLISHER
        and item.author_id == user.id
        and item.status.value == "draft"
    )


def valid_text(value, maximum=None):
    return (
        isinstance(value, str)
        and bool(value.strip())
        and (maximum is None or len(value.strip()) <= maximum)
    )


def valid_slug(value, maximum=255):
    return valid_text(value, maximum) and SLUG_PATTERN.fullmatch(value.strip()) is not None


def parse_datetime(value):
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError
    return parsed


def published_at_for(status, current=None):
    if status.value == "published":
        return current or datetime.now(timezone.utc)
    return None


def iso(value):
    return value.isoformat() if value is not None else None
