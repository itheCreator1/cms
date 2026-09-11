from datetime import datetime, timedelta, timezone

import pytest
from flask_jwt_extended import create_access_token
from flask_migrate import upgrade
from sqlalchemy import text


class ContentTestConfig:
    TESTING = True
    SECRET_KEY = "content-test-secret"
    JWT_SECRET_KEY = "content-jwt-test-secret-at-least-32-bytes"
    JWT_TOKEN_LOCATION = ["headers"]
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FRONTEND_ORIGIN = "http://frontend.test"
    RATELIMIT_ENABLED = False


@pytest.fixture(scope="module")
def app(postgres_database_url):
    from backend.app import create_app

    ContentTestConfig.SQLALCHEMY_DATABASE_URI = postgres_database_url
    application = create_app(ContentTestConfig)
    with application.app_context():
        upgrade(directory="migrations")
    return application


@pytest.fixture(autouse=True)
def clean_database(app):
    from backend.extensions import db

    with app.app_context():
        db.session.execute(
            text(
                "TRUNCATE TABLE article_tags, articles, announcements, pages, "
                "media, tags, categories, users RESTART IDENTITY CASCADE"
            )
        )
        db.session.commit()
    yield
    with app.app_context():
        db.session.rollback()
        db.session.execute(
            text(
                "TRUNCATE TABLE article_tags, articles, announcements, pages, "
                "media, tags, categories, users RESTART IDENTITY CASCADE"
            )
        )
        db.session.commit()
        db.session.remove()


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
            identity=str(user_id), additional_claims={"role": role}
        )
    return {"Authorization": f"Bearer {token}"}


def seed_relations(app, uploader_id):
    from backend.extensions import db
    from backend.models import Category, Media, Tag

    with app.app_context():
        category = Category(name="News", slug="news")
        tag = Tag(name="Featured", slug="featured")
        media = Media(
            filename="lead.jpg",
            url="/uploads/lead.jpg",
            uploaded_by=uploader_id,
            file_type="image/jpeg",
        )
        db.session.add_all([category, tag, media])
        db.session.commit()
        return category.id, tag.id, media.id


def article_payload(category_id, **overrides):
    return {
        "title": "A useful headline",
        "slug": "useful-headline",
        "body": "Complete article body",
        "category_id": category_id,
        **overrides,
    }


def test_anonymous_reads_return_only_published_content_and_invalid_tokens_fail(
    app, client
):
    from backend.extensions import db
    from backend.models import (
        Announcement,
        AnnouncementStatus,
        Article,
        ArticleStatus,
        Category,
        Page,
        PageStatus,
    )

    author_id = create_user(app, "author@example.test", "publisher")
    with app.app_context():
        category = Category(name="News", slug="news")
        db.session.add(category)
        db.session.flush()
        db.session.add_all(
            [
                Article(title="Public", slug="public", body="Published", status=ArticleStatus.PUBLISHED, author_id=author_id, category_id=category.id, published_at=datetime.now(timezone.utc)),
                Article(title="Private", slug="private", body="Draft", author_id=author_id, category_id=category.id),
                Announcement(title="Current", body="Published", status=AnnouncementStatus.PUBLISHED, author_id=author_id, published_at=datetime.now(timezone.utc)),
                Announcement(title="Expired", body="Old", status=AnnouncementStatus.PUBLISHED, author_id=author_id, published_at=datetime.now(timezone.utc), expires_at=datetime.now(timezone.utc) - timedelta(minutes=1)),
                Page(title="About", slug="about", body="Public page", status=PageStatus.PUBLISHED, author_id=author_id),
                Page(title="Hidden", slug="hidden", body="Draft page", author_id=author_id),
            ]
        )
        db.session.commit()

    assert [item["slug"] for item in client.get("/api/articles").json["items"]] == ["public"]
    assert [item["title"] for item in client.get("/api/announcements").json["items"]] == ["Current"]
    assert [item["slug"] for item in client.get("/api/pages").json["items"]] == ["about"]
    assert client.get("/api/articles/slug/private").status_code == 404
    assert client.get("/api/pages/slug/hidden").status_code == 404
    invalid = client.get("/api/articles", headers={"Authorization": "Bearer malformed"})
    assert invalid.status_code == 401
    assert invalid.json == {"error": "Authentication required"}


def test_publisher_creates_and_submits_own_article_with_server_owned_fields(app, client):
    owner_id = create_user(app, "owner@example.test", "publisher")
    other_id = create_user(app, "other@example.test", "publisher")
    category_id, tag_id, media_id = seed_relations(app, owner_id)
    headers = bearer(app, owner_id, "publisher")
    created = client.post(
        "/api/articles",
        headers=headers,
        json=article_payload(category_id, author_id=other_id, tag_ids=[tag_id], featured_image_id=media_id),
    )
    assert created.status_code == 201
    item = created.json["item"]
    assert (item["author_id"], item["status"], item["tag_ids"]) == (owner_id, "draft", [tag_id])

    submitted = client.put(
        f"/api/articles/{item['id']}",
        headers=headers,
        json={"title": "Revised", "status": "pending_review"},
    )
    assert submitted.status_code == 200
    assert submitted.json["item"]["status"] == "pending_review"
    assert client.put(f"/api/articles/{item['id']}", headers=headers, json={"title": "Denied"}).status_code == 403
    assert client.delete(f"/api/articles/{item['id']}", headers=headers).status_code == 403


def test_article_body_blocks_are_returned_in_order_and_project_to_plain_text(app, client):
    publisher_id = create_user(app, "blocks@example.test", "publisher")
    category_id, _, media_id = seed_relations(app, publisher_id)

    payload = article_payload(category_id)
    payload.pop("body")
    payload["body_blocks"] = [
        {"type": "text", "text": "Opening paragraph"},
        {"type": "image", "media_id": media_id},
        {"type": "text", "text": "Closing paragraph"},
    ]
    response = client.post(
        "/api/articles",
        headers=bearer(app, publisher_id, "publisher"),
        json=payload,
    )

    assert response.status_code == 201
    assert response.json["item"]["body"] == "Opening paragraph\n\nClosing paragraph"
    blocks = response.json["item"]["body_blocks"]
    assert [
        {key: value for key, value in block.items() if key != "media"}
        for block in blocks
    ] == [
        {"type": "text", "text": "Opening paragraph"},
        {"type": "image", "media_id": media_id},
        {"type": "text", "text": "Closing paragraph"},
    ]
    assert blocks[1]["media"]["id"] == media_id


def test_content_rejects_body_and_body_blocks_together(app, client):
    publisher_id = create_user(app, "ambiguous@example.test", "publisher")
    category_id, _, _ = seed_relations(app, publisher_id)

    response = client.post(
        "/api/articles",
        headers=bearer(app, publisher_id, "publisher"),
        json=article_payload(
            category_id,
            body_blocks=[{"type": "text", "text": "A different body"}],
        ),
    )

    assert response.status_code == 400
    assert response.json == {"error": "Invalid content data"}


def test_repeated_block_replacement_preserves_order(app, client):
    owner = create_user(app, "replacement@example.test", "publisher")
    category, _, image = seed_relations(app, owner)
    headers = bearer(app, owner, "publisher")
    item = client.post("/api/articles", headers=headers, json=article_payload(category)).json["item"]
    for blocks in (
        [{"type": "text", "text": "First"}, {"type": "image", "media_id": image}],
        [{"type": "image", "media_id": image}, {"type": "text", "text": "Second"}],
        [{"type": "text", "text": "Final"}],
    ):
        response = client.put(f"/api/articles/{item['id']}", headers=headers, json={"body_blocks": blocks})
        assert response.status_code == 200
        assert [{k: v for k, v in block.items() if k != "media"} for block in response.json["item"]["body_blocks"]] == blocks


def test_duplicate_slug_during_block_replacement_returns_conflict_without_changes(app, client):
    owner = create_user(app, "atomic-replacement@example.test", "publisher")
    category, _, _ = seed_relations(app, owner)
    headers = bearer(app, owner, "publisher")
    original = client.post(
        "/api/articles", headers=headers, json=article_payload(category, slug="original")
    ).json["item"]
    client.post(
        "/api/articles", headers=headers, json=article_payload(category, slug="taken")
    )

    response = client.put(
        f"/api/articles/{original['id']}",
        headers=headers,
        json={
            "slug": "taken",
            "body_blocks": [{"type": "text", "text": "Replacement text"}],
        },
    )

    assert response.status_code == 409
    stored = client.get(f"/api/articles/{original['id']}", headers=headers).json["item"]
    assert stored["slug"] == "original"
    assert stored["body_blocks"] == [{"type": "text", "text": "Complete article body"}]


def test_body_only_article_write_remains_a_single_text_block(app, client):
    publisher_id = create_user(app, "legacy-body@example.test", "publisher")
    category_id, _, _ = seed_relations(app, publisher_id)

    response = client.post(
        "/api/articles",
        headers=bearer(app, publisher_id, "publisher"),
        json=article_payload(category_id, body="Legacy client body"),
    )

    assert response.status_code == 201
    assert response.json["item"]["body_blocks"] == [
        {"type": "text", "text": "Legacy client body"}
    ]


def test_publisher_cannot_mutate_foreign_article_or_publish_content(app, client):
    owner_id = create_user(app, "owner@example.test", "publisher")
    other_id = create_user(app, "other@example.test", "publisher")
    category_id, _, _ = seed_relations(app, owner_id)
    article = client.post(
        "/api/articles",
        headers=bearer(app, owner_id, "publisher"),
        json=article_payload(category_id),
    ).json["item"]
    other_headers = bearer(app, other_id, "publisher")
    assert client.put(f"/api/articles/{article['id']}", headers=other_headers, json={"title": "Denied"}).status_code == 403
    assert client.put(f"/api/articles/{article['id']}", headers=bearer(app, owner_id, "publisher"), json={"status": "published"}).status_code == 403


def test_publisher_cannot_attach_another_publishers_images(app, client):
    from backend.extensions import db
    from backend.models import Media

    owner_id = create_user(app, "image-owner@example.test", "publisher")
    other_id = create_user(app, "image-other@example.test", "publisher")
    category_id, _, _ = seed_relations(app, owner_id)
    with app.app_context():
        foreign_image = Media(
            filename="foreign.jpg",
            url="/uploads/foreign.jpg",
            uploaded_by=other_id,
            file_type="image/jpeg",
        )
        db.session.add(foreign_image)
        db.session.commit()
        foreign_image_id = foreign_image.id

    featured = client.post(
        "/api/articles",
        headers=bearer(app, owner_id, "publisher"),
        json=article_payload(category_id, featured_image_id=foreign_image_id),
    )
    inline_payload = article_payload(category_id, slug="foreign-inline")
    inline_payload.pop("body")
    inline_payload["body_blocks"] = [
        {"type": "text", "text": "Body"},
        {"type": "image", "media_id": foreign_image_id},
    ]
    inline = client.post(
        "/api/articles",
        headers=bearer(app, owner_id, "publisher"),
        json=inline_payload,
    )

    assert featured.status_code == 400
    assert inline.status_code == 400


def test_admin_manages_any_article_and_controls_publication_timestamps(app, client):
    publisher_id = create_user(app, "publisher@example.test", "publisher")
    admin_id = create_user(app, "admin@example.test", "admin")
    category_id, _, _ = seed_relations(app, admin_id)
    article = client.post("/api/articles", headers=bearer(app, publisher_id, "publisher"), json=article_payload(category_id)).json["item"]
    headers = bearer(app, admin_id, "admin")
    published = client.put(f"/api/articles/{article['id']}", headers=headers, json={"status": "published"})
    assert published.status_code == 200
    assert published.json["item"]["published_at"] is not None
    unpublished = client.put(f"/api/articles/{article['id']}", headers=headers, json={"status": "draft"})
    assert unpublished.json["item"]["published_at"] is None
    assert client.delete(f"/api/articles/{article['id']}", headers=headers).status_code == 204


def test_publisher_submits_own_draft_announcement_but_cannot_publish_or_manage_pages(app, client):
    publisher_id = create_user(app, "publisher@example.test", "publisher")
    headers = bearer(app, publisher_id, "publisher")
    created = client.post("/api/announcements", headers=headers, json={"title": "Notice", "body": "Details"})
    assert created.status_code == 201
    item = created.json["item"]
    assert (item["author_id"], item["status"]) == (publisher_id, "draft")
    submitted = client.put(
        f"/api/announcements/{item['id']}",
        headers=headers,
        json={"status": "pending_review"},
    )
    assert submitted.status_code == 200
    assert submitted.json["item"]["status"] == "pending_review"
    assert client.put(f"/api/announcements/{item['id']}", headers=headers, json={"status": "published"}).status_code == 403
    assert client.post("/api/pages", headers=headers, json={"title": "About", "slug": "about", "body": "Body"}).status_code == 403


def test_admin_crud_for_pages_is_published_only_to_anonymous_users(app, client):
    admin_id = create_user(app, "admin@example.test", "admin")
    headers = bearer(app, admin_id, "admin")
    created = client.post("/api/pages", headers=headers, json={"title": "About", "slug": "about", "body": "Body"})
    assert created.status_code == 201
    page_id = created.json["item"]["id"]
    assert client.get("/api/pages/slug/about").status_code == 404
    assert client.put(f"/api/pages/{page_id}", headers=headers, json={"status": "published"}).status_code == 200
    assert client.get("/api/pages/slug/about").json["item"]["slug"] == "about"
    assert client.delete(f"/api/pages/{page_id}", headers=headers).status_code == 204


@pytest.mark.parametrize(
    "endpoint,payload",
    [
        ("/api/articles", {"title": "Missing relationships", "slug": "bad", "body": "Body"}),
        ("/api/announcements", {"title": "", "body": "Body"}),
        ("/api/pages", {"title": "Page", "slug": "bad slug", "body": "Body"}),
    ],
)
def test_content_create_rejects_invalid_payloads_with_safe_json(app, client, endpoint, payload):
    admin_id = create_user(app, f"admin-{endpoint.rsplit('/', 1)[-1]}@example.test", "admin")
    response = client.post(endpoint, headers=bearer(app, admin_id, "admin"), json=payload)
    assert response.status_code == 400
    assert response.json == {"error": "Invalid content data"}


def test_duplicate_slug_and_unknown_relationships_are_safe_errors(app, client):
    admin_id = create_user(app, "admin@example.test", "admin")
    category_id, _, _ = seed_relations(app, admin_id)
    headers = bearer(app, admin_id, "admin")
    assert client.post("/api/articles", headers=headers, json=article_payload(category_id)).status_code == 201
    duplicate = client.post("/api/articles", headers=headers, json=article_payload(category_id))
    assert duplicate.status_code == 409
    assert duplicate.json == {"error": "Slug is already in use"}
    unknown = client.post("/api/articles", headers=headers, json=article_payload(category_id, slug="unknown", tag_ids=[9999]))
    assert unknown.status_code == 400
    assert unknown.json == {"error": "Invalid content data"}
