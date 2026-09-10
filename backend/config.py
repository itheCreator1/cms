import os
from datetime import timedelta
from pathlib import Path


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "development-only-change-me")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", "postgresql+psycopg://cms:cms@db:5432/cms"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        seconds=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES_SECONDS", "900"))
    )
    JWT_TOKEN_LOCATION = ["headers"]
    JWT_HEADER_TYPE = "Bearer"
    RATELIMIT_STORAGE_URI = "memory://"
    MEDIA_STORAGE_ROOT = os.getenv(
        "MEDIA_STORAGE_ROOT",
        str(Path(__file__).resolve().parent.parent / "var" / "media"),
    )
    MEDIA_MAX_BYTES = int(os.getenv("MEDIA_MAX_BYTES", str(10 * 1024 * 1024)))
    MEDIA_MAX_PIXELS = int(os.getenv("MEDIA_MAX_PIXELS", "40000000"))
    MAX_CONTENT_LENGTH = MEDIA_MAX_BYTES + 1024 * 1024
