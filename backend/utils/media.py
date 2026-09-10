import ipaddress
import unicodedata
from urllib.parse import urlsplit, urlunsplit

from backend.utils.content import iso


def serialize_media(item):
    return {
        "id": item.id,
        "filename": item.filename,
        "url": item.url,
        "uploaded_by": item.uploaded_by,
        "uploaded_at": iso(item.uploaded_at),
        "file_type": item.file_type,
        "source_type": item.source_type,
        "media_type": item.media_type,
        "provider": item.provider,
        "alt_text": item.alt_text,
    }


def normalize_alt_text(value):
    if value is None or value == "":
        return None
    if not isinstance(value, str):
        raise ValueError
    value = value.strip()
    if not value or len(value) > 500:
        raise ValueError
    if any(unicodedata.category(character).startswith("C") for character in value):
        raise ValueError
    return value


def normalize_external_url(value):
    if not isinstance(value, str) or not value or len(value) > 2048:
        raise ValueError
    if value != value.strip() or any(
        unicodedata.category(character).startswith("C") for character in value
    ):
        raise ValueError
    try:
        parsed = urlsplit(value)
        if parsed.scheme.casefold() != "https" or not parsed.hostname:
            raise ValueError
        if parsed.username is not None or parsed.password is not None:
            raise ValueError
        host = parsed.hostname.encode("idna").decode("ascii").casefold()
        if host == "localhost" or host.endswith(".local"):
            raise ValueError
        try:
            address = ipaddress.ip_address(host)
        except ValueError:
            if "." not in host:
                raise ValueError
        else:
            if not address.is_global:
                raise ValueError
        port = parsed.port
    except (UnicodeError, ValueError):
        raise ValueError from None

    netloc = host if port is None else f"{host}:{port}"
    normalized = urlunsplit(("https", netloc, parsed.path or "/", parsed.query, ""))
    provider, media_type = classify_provider(host)
    return normalized, host, provider, media_type


def classify_provider(host):
    if _matches_domain(host, "youtube.com") or host == "youtu.be":
        return "youtube", "video"
    if _matches_domain(host, "instagram.com"):
        return "instagram", "social"
    if _matches_domain(host, "facebook.com") or host == "fb.watch":
        return "facebook", "social"
    return "generic", "link"


def _matches_domain(host, domain):
    return host == domain or host.endswith(f".{domain}")
