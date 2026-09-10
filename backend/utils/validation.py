import re
import unicodedata


EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MAX_EMAIL_LENGTH = 255


def normalize_email(value):
    if not isinstance(value, str):
        return None
    if any(unicodedata.category(character).startswith("C") for character in value):
        return None

    email = value.strip().casefold()
    if not email or len(email) > MAX_EMAIL_LENGTH:
        return None
    if not EMAIL_PATTERN.fullmatch(email):
        return None
    return email
