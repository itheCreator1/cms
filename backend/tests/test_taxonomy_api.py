import pytest
from flask_jwt_extended import create_access_token
from flask_migrate import upgrade
from sqlalchemy import text


class TaxonomyTestConfig:
    TESTING = True
    SECRET_KEY = "taxonomy-test-secret"
    JWT_SECRET_KEY = "taxonomy-jwt-test-secret-at-least-32-bytes"
    JWT_TOKEN_LOCATION = ["headers"]
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FRONTEND_ORIGIN = "http://frontend.test"
    RATELIMIT_ENABLED = False


@pytest.fixture(scope="module")
def app(postgres_database_url):
    from backend.app import create_app

    TaxonomyTestConfig.SQLALCHEMY_DATABASE_URI = postgres_database_url
    application = create_app(TaxonomyTestConfig)
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
    yield
    with app.app_context():
        db.session.rollback()
        db.session.execute(text(f"TRUNCATE TABLE {tables} RESTART IDENTITY CASCADE"))
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
            identity=str(user_id),
            additional_claims={"role": role, "auth_channel": "regular"},
        )
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.parametrize("resource", ["categories", "tags"])
def test_taxonomy_is_publicly_readable_and_admin_managed(app, client, resource):
    publisher_id = create_user(app, f"{resource}@example.test", "publisher")
    admin_id = create_user(app, f"admin-{resource}@example.test", "admin")
    payload = {"name": "Local News", "slug": "local-news"}

    denied = client.post(
        f"/api/{resource}",
        headers=bearer(app, publisher_id, "publisher"),
        json=payload,
    )
    assert denied.status_code == 403

    created = client.post(
        f"/api/{resource}",
        headers=bearer(app, admin_id, "admin"),
        json=payload,
    )
    assert created.status_code == 201
    assert created.json == {
        "item": {"id": created.json["item"]["id"], **payload}
    }
    item_id = created.json["item"]["id"]

    assert client.get(f"/api/{resource}").json == {
        "items": [{"id": item_id, **payload}]
    }
    assert client.get(f"/api/{resource}/{item_id}").json == {
        "item": {"id": item_id, **payload}
    }

    updated = client.put(
        f"/api/{resource}/{item_id}",
        headers=bearer(app, admin_id, "admin"),
        json={"name": "Regional News"},
    )
    assert updated.status_code == 200
    assert updated.json["item"]["name"] == "Regional News"

    assert (
        client.delete(
            f"/api/{resource}/{item_id}",
            headers=bearer(app, admin_id, "admin"),
        ).status_code
        == 204
    )
    assert client.get(f"/api/{resource}/{item_id}").status_code == 404


@pytest.mark.parametrize("resource", ["categories", "tags"])
def test_taxonomy_rejects_invalid_and_duplicate_values(app, client, resource):
    admin_id = create_user(app, f"validation-{resource}@example.test", "admin")
    headers = bearer(app, admin_id, "admin")

    invalid = client.post(
        f"/api/{resource}", headers=headers, json={"name": " ", "slug": "Bad Slug"}
    )
    assert invalid.status_code == 400
    assert invalid.json == {"error": "Invalid taxonomy data"}

    assert client.post(
        f"/api/{resource}",
        headers=headers,
        json={"name": "News", "slug": "news"},
    ).status_code == 201
    duplicate = client.post(
        f"/api/{resource}",
        headers=headers,
        json={"name": "News", "slug": "different"},
    )
    assert duplicate.status_code == 409
    assert duplicate.json == {"error": "Name or slug is already in use"}


def test_referenced_taxonomy_cannot_be_deleted(app, client):
    from backend.extensions import db
    from backend.models import Article, Category, Tag

    admin_id = create_user(app, "referenced-taxonomy@example.test", "admin")
    with app.app_context():
        category = Category(name="Required", slug="required")
        tag = Tag(name="Attached", slug="attached")
        article = Article(
            title="Retained",
            slug="retained",
            body="Body",
            author_id=admin_id,
            category=category,
            tags=[tag],
        )
        db.session.add(article)
        db.session.commit()
        category_id, tag_id = category.id, tag.id

    headers = bearer(app, admin_id, "admin")
    for resource, item_id in (("categories", category_id), ("tags", tag_id)):
        response = client.delete(f"/api/{resource}/{item_id}", headers=headers)
        assert response.status_code == 409
        assert response.json == {"error": "Resource is in use"}
