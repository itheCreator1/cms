import base64
import io

import pytest
from flask_jwt_extended import create_access_token
from flask_migrate import upgrade
from sqlalchemy import text


PNG_1X1 = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
)


class MediaTestConfig:
    TESTING = True
    SECRET_KEY = "media-test-secret"
    JWT_SECRET_KEY = "media-jwt-test-secret-at-least-32-bytes"
    JWT_TOKEN_LOCATION = ["headers"]
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FRONTEND_ORIGIN = "http://frontend.test"
    RATELIMIT_ENABLED = False
    MEDIA_MAX_BYTES = 1024
    MEDIA_MAX_PIXELS = 40_000_000
    MAX_CONTENT_LENGTH = 2048


@pytest.fixture(scope="module")
def app(postgres_database_url, tmp_path_factory):
    from backend.app import create_app

    MediaTestConfig.SQLALCHEMY_DATABASE_URI = postgres_database_url
    MediaTestConfig.MEDIA_STORAGE_ROOT = str(tmp_path_factory.mktemp("media"))
    application = create_app(MediaTestConfig)
    with application.app_context():
        upgrade(directory="migrations")
    return application


@pytest.fixture(autouse=True)
def clean_database(app):
    from backend.extensions import db

    tables = (
        "article_tags, articles, announcements, pages, media, tags, "
        "categories, users"
    )
    with app.app_context():
        db.session.execute(text(f"TRUNCATE TABLE {tables} RESTART IDENTITY CASCADE"))
        db.session.commit()
    storage = app.config["MEDIA_STORAGE_ROOT"]
    for child in __import__("pathlib").Path(storage).iterdir():
        child.unlink()
    yield
    with app.app_context():
        db.session.rollback()
        db.session.execute(text(f"TRUNCATE TABLE {tables} RESTART IDENTITY CASCADE"))
        db.session.commit()
        db.session.remove()
    for child in __import__("pathlib").Path(storage).iterdir():
        child.unlink()


@pytest.fixture()
def client(app):
    return app.test_client()


def create_user(app, email, role):
    from backend.extensions import db
    from backend.models import User, UserRole

    with app.app_context():
        user = User(email=email, role=UserRole(role))
        user.set_password("correct horse battery staple")
        db.session.add(user)
        db.session.commit()
        return user.id


def bearer(app, user_id, role):
    with app.app_context():
        token = create_access_token(
            identity=str(user_id),
            additional_claims={"role": role, "auth_channel": "regular"},
        )
    return {"Authorization": f"Bearer {token}"}


def upload(client, headers, content=PNG_1X1, filename="pixel.png", alt_text="Pixel"):
    return client.post(
        "/api/media/uploads",
        headers=headers,
        data={"file": (io.BytesIO(content), filename), "alt_text": alt_text},
        content_type="multipart/form-data",
    )


def animated_gif():
    from PIL import Image

    output = io.BytesIO()
    frames = [Image.new("RGB", (1, 1), color) for color in ("red", "blue")]
    frames[0].save(
        output,
        format="GIF",
        save_all=True,
        append_images=frames[1:],
        duration=100,
        loop=0,
    )
    return output.getvalue()


def test_admin_uploads_serves_updates_and_deletes_image(app, client):
    publisher_id = create_user(app, "media-publisher@example.test", "publisher")
    admin_id = create_user(app, "media-admin@example.test", "admin")
    headers = bearer(app, admin_id, "admin")
    created = upload(client, headers)
    assert created.status_code == 201
    item = created.json["item"]
    assert item == {
        "id": item["id"],
        "filename": "pixel.png",
        "url": item["url"],
        "uploaded_by": admin_id,
        "uploaded_at": item["uploaded_at"],
        "file_type": "image/png",
        "source_type": "upload",
        "media_type": "image",
        "provider": "local",
        "alt_text": "Pixel",
    }
    assert item["url"].startswith("/api/media/files/")
    assert "pixel.png" not in item["url"]

    assert client.get("/api/media").status_code == 401
    assert client.get("/api/media", headers=headers).json["items"] == [item]
    assert client.get(f"/api/media/{item['id']}", headers=headers).json == {
        "item": item
    }

    served = client.get(item["url"], headers=headers)
    assert served.status_code == 200
    assert served.content_type == "image/png"
    assert served.headers["X-Content-Type-Options"] == "nosniff"

    updated = client.put(
        f"/api/media/{item['id']}", headers=headers, json={"alt_text": "Dot"}
    )
    assert updated.status_code == 200
    assert updated.json["item"]["alt_text"] == "Dot"
    assert client.put(
        f"/api/media/{item['id']}", headers=headers, json={"url": "https://example.test"}
    ).status_code == 400

    assert client.delete(f"/api/media/{item['id']}", headers=headers).status_code == 204
    assert client.get(item["url"]).status_code == 404


def test_publisher_uploads_own_images_and_private_files_require_authorization(app, client):
    publisher_id = create_user(app, "picture-owner@example.test", "publisher")
    other_publisher_id = create_user(app, "picture-other@example.test", "publisher")
    admin_id = create_user(app, "picture-admin@example.test", "admin")
    publisher_headers = bearer(app, publisher_id, "publisher")
    item = upload(client, publisher_headers).json["item"]

    assert client.get("/api/media", headers=publisher_headers).json["items"] == [item]
    assert client.get("/api/media", headers=bearer(app, other_publisher_id, "publisher")).json["items"] == []
    assert client.get(f"/api/media/{item['id']}", headers=bearer(app, other_publisher_id, "publisher")).status_code == 404
    assert client.get(item["url"]).status_code == 404
    assert client.get(item["url"], headers=bearer(app, other_publisher_id, "publisher")).status_code == 404

    owner_file = client.get(item["url"], headers=publisher_headers)
    assert owner_file.status_code == 200
    assert owner_file.headers["Cache-Control"] == "no-store"
    assert client.get(item["url"], headers=bearer(app, admin_id, "admin")).status_code == 200


def test_published_content_grants_public_image_access_until_unpublished(app, client):
    from backend.extensions import db
    from backend.models import Category

    publisher_id = create_user(app, "publication-owner@example.test", "publisher")
    admin_id = create_user(app, "publication-admin@example.test", "admin")
    publisher_headers = bearer(app, publisher_id, "publisher")
    image = upload(client, publisher_headers).json["item"]
    with app.app_context():
        category = Category(name="Publication", slug="publication")
        db.session.add(category)
        db.session.commit()
        category_id = category.id

    article = client.post(
        "/api/articles",
        headers=publisher_headers,
        json={
            "title": "Published picture",
            "slug": "published-picture",
            "body": "Story body",
            "category_id": category_id,
            "featured_image_id": image["id"],
        },
    ).json["item"]
    admin_headers = bearer(app, admin_id, "admin")
    assert client.put(
        f"/api/articles/{article['id']}", headers=admin_headers, json={"status": "published"}
    ).status_code == 200
    assert client.get(image["url"]).status_code == 200

    assert client.put(
        f"/api/articles/{article['id']}", headers=admin_headers, json={"status": "draft"}
    ).status_code == 200
    assert client.get(image["url"]).status_code == 404


def test_upload_rejects_untrusted_or_oversized_images(app, client):
    admin_id = create_user(app, "unsafe-media@example.test", "admin")
    headers = bearer(app, admin_id, "admin")

    for content, filename in (
        (b"not an image", "fake.png"),
        (b"<svg xmlns='http://www.w3.org/2000/svg'></svg>", "active.svg"),
        (animated_gif(), "animated.gif"),
    ):
        response = upload(client, headers, content, filename)
        assert response.status_code == 400
        assert response.json == {"error": "Invalid media data"}

    oversized = upload(client, headers, b"x" * 1025, "large.png")
    assert oversized.status_code == 413
    assert oversized.json == {"error": "Upload too large"}


def test_admin_manages_external_https_links_without_embed_html(app, client):
    admin_id = create_user(app, "links@example.test", "admin")
    headers = bearer(app, admin_id, "admin")

    created = client.post(
        "/api/media/links",
        headers=headers,
        json={
            "url": "https://WWW.YouTube.com/watch?v=abc#section",
            "alt_text": "Project video",
        },
    )
    assert created.status_code == 201
    item = created.json["item"]
    assert item["url"] == "https://www.youtube.com/watch?v=abc"
    assert item["filename"] == "www.youtube.com"
    assert item["file_type"] == "text/uri-list"
    assert item["source_type"] == "external"
    assert item["media_type"] == "video"
    assert item["provider"] == "youtube"

    updated = client.put(
        f"/api/media/{item['id']}",
        headers=headers,
        json={"url": "https://instagram.com/p/example", "alt_text": "Post"},
    )
    assert updated.status_code == 200
    assert updated.json["item"]["provider"] == "instagram"
    assert updated.json["item"]["media_type"] == "social"

    duplicate = client.post(
        "/api/media/links",
        headers=headers,
        json={"url": "https://instagram.com/p/example"},
    )
    assert duplicate.status_code == 409
    assert duplicate.json == {"error": "Media URL is already in use"}


@pytest.mark.parametrize(
    "url",
    [
        "http://youtube.com/watch?v=abc",
        "https://user:password@example.com/file",
        "https:///missing-host",
        "<iframe src='https://youtube.com/embed/abc'></iframe>",
        "https://example.com/\nheader",
    ],
)
def test_external_media_rejects_unsafe_urls(app, client, url):
    admin_id = create_user(app, f"invalid-{abs(hash(url))}@example.test", "admin")
    response = client.post(
        "/api/media/links",
        headers=bearer(app, admin_id, "admin"),
        json={"url": url},
    )
    assert response.status_code == 400
    assert response.json == {"error": "Invalid media data"}


def test_referenced_media_cannot_be_deleted_or_used_as_featured_link(app, client):
    from backend.extensions import db
    from backend.models import Category

    admin_id = create_user(app, "referenced-media@example.test", "admin")
    headers = bearer(app, admin_id, "admin")
    upload_item = upload(client, headers).json["item"]
    link_item = client.post(
        "/api/media/links",
        headers=headers,
        json={"url": "https://example.com/story"},
    ).json["item"]
    with app.app_context():
        category = Category(name="Media", slug="media")
        db.session.add(category)
        db.session.commit()
        category_id = category.id

    invalid_feature = client.post(
        "/api/articles",
        headers=headers,
        json={
            "title": "External feature",
            "slug": "external-feature",
            "body": "Body",
            "category_id": category_id,
            "featured_image_id": link_item["id"],
        },
    )
    assert invalid_feature.status_code == 400

    assert client.post(
        "/api/articles",
        headers=headers,
        json={
            "title": "Uploaded feature",
            "slug": "uploaded-feature",
            "body": "Body",
            "category_id": category_id,
            "featured_image_id": upload_item["id"],
        },
    ).status_code == 201
    conflict = client.delete(f"/api/media/{upload_item['id']}", headers=headers)
    assert conflict.status_code == 409
    assert conflict.json == {"error": "Resource is in use"}
