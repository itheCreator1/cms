import pytest
from flask_jwt_extended import create_access_token
from flask_migrate import upgrade
from sqlalchemy import text


class UsersTestConfig:
    TESTING = True
    SECRET_KEY = "users-test-secret"
    JWT_SECRET_KEY = "users-jwt-test-secret-at-least-32-bytes"
    JWT_TOKEN_LOCATION = ["headers"]
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FRONTEND_ORIGIN = "http://frontend.test"
    RATELIMIT_ENABLED = False


@pytest.fixture(scope="module")
def app(postgres_database_url):
    from backend.app import create_app

    UsersTestConfig.SQLALCHEMY_DATABASE_URI = postgres_database_url
    application = create_app(UsersTestConfig)
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


def create_user(app, email, role, password="correct horse battery staple"):
    from backend.extensions import db
    from backend.models import User, UserRole

    with app.app_context():
        user = User(email=email, role=UserRole(role))
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user.id


def bearer_for(app, user_id, role):
    channel = "superadmin" if role == "superadmin" else "regular"
    with app.app_context():
        token = create_access_token(
            identity=str(user_id),
            additional_claims={"role": role, "auth_channel": channel},
        )
    return {"Authorization": f"Bearer {token}"}


def test_admin_crud_is_limited_to_publishers(app, client):
    admin_id = create_user(app, "admin@example.test", "admin")
    visitor_id = create_user(app, "visitor@example.test", "visitor")
    other_admin_id = create_user(app, "other-admin@example.test", "admin")
    headers = bearer_for(app, admin_id, "admin")

    created = client.post(
        "/api/users",
        headers=headers,
        json={
            "email": " New.Publisher@Example.TEST ",
            "password": "publisher password",
            "role": "publisher",
        },
    )
    assert created.status_code == 201
    item = created.json["item"]
    assert set(item) == {"id", "email", "role", "created_at"}
    assert item["email"] == "new.publisher@example.test"
    assert item["role"] == "publisher"
    assert "password" not in created.get_data(as_text=True).lower()

    listed = client.get("/api/users", headers=headers)
    assert listed.status_code == 200
    assert [user["id"] for user in listed.json["items"]] == [item["id"]]
    assert client.get(f"/api/users/{item['id']}", headers=headers).status_code == 200
    assert client.get(f"/api/users/{visitor_id}", headers=headers).status_code == 403
    assert client.get(f"/api/users/{other_admin_id}", headers=headers).status_code == 403

    updated = client.put(
        f"/api/users/{item['id']}",
        headers=headers,
        json={"email": "updated@example.test", "password": "updated password"},
    )
    assert updated.status_code == 200
    assert updated.json["item"]["email"] == "updated@example.test"
    with app.app_context():
        from backend.extensions import db
        from backend.models import User

        user = db.session.get(User, item["id"])
        assert user.check_password("updated password")
        assert "updated password" not in user.password_hash

    escalation = client.put(
        f"/api/users/{item['id']}", headers=headers, json={"role": "admin"}
    )
    assert escalation.status_code == 403
    assert escalation.json == {"error": "Insufficient permissions"}
    create_admin = client.post(
        "/api/users",
        headers=headers,
        json={
            "email": "forbidden-admin@example.test",
            "password": "forbidden password",
            "role": "admin",
        },
    )
    assert create_admin.status_code == 403

    assert client.delete(f"/api/users/{item['id']}", headers=headers).status_code == 204


def test_superadmin_manages_all_roles_but_cannot_demote_or_delete_self(app, client):
    root_id = create_user(app, "root@example.test", "superadmin")
    visitor_id = create_user(app, "managed-visitor@example.test", "visitor")
    headers = bearer_for(app, root_id, "superadmin")

    created = client.post(
        "/api/users",
        headers=headers,
        json={
            "email": "created-admin@example.test",
            "password": "created admin password",
            "role": "admin",
        },
    )
    assert created.status_code == 201
    assert created.json["item"]["role"] == "admin"
    assert {item["role"] for item in client.get("/api/users", headers=headers).json["items"]} == {
        "visitor",
        "admin",
        "superadmin",
    }

    promoted = client.put(
        f"/api/users/{visitor_id}", headers=headers, json={"role": "publisher"}
    )
    assert promoted.status_code == 200
    assert promoted.json["item"]["role"] == "publisher"

    for method, payload in (("put", {"role": "admin"}), ("delete", None)):
        response = getattr(client, method)(
            f"/api/users/{root_id}", headers=headers, json=payload
        )
        assert response.status_code == 409
        assert response.json == {"error": "Active Superadmin account is protected"}


def test_user_validation_duplicate_email_and_authentication_boundaries(app, client):
    publisher_id = create_user(app, "publisher@example.test", "publisher")
    root_id = create_user(app, "validation-root@example.test", "superadmin")
    headers = bearer_for(app, root_id, "superadmin")

    assert client.get("/api/users").status_code == 401
    assert client.get(
        "/api/users", headers=bearer_for(app, publisher_id, "publisher")
    ).status_code == 403
    invalid = client.post(
        "/api/users",
        headers=headers,
        json={"email": "bad", "password": "short", "role": "editor"},
    )
    assert invalid.status_code == 400
    assert invalid.json == {"error": "Invalid user data"}

    duplicate = client.post(
        "/api/users",
        headers=headers,
        json={
            "email": "publisher@example.test",
            "password": "another password",
            "role": "publisher",
        },
    )
    assert duplicate.status_code == 409
    assert duplicate.json == {"error": "Email is already registered"}


def test_referenced_user_cannot_be_deleted(app, client):
    from backend.extensions import db
    from backend.models import Article, Category

    root_id = create_user(app, "delete-root@example.test", "superadmin")
    publisher_id = create_user(app, "author@example.test", "publisher")
    with app.app_context():
        article = Article(
            title="Retained",
            slug="retained-user-content",
            body="Body",
            author_id=publisher_id,
            category=Category(name="Required", slug="required"),
        )
        db.session.add(article)
        db.session.commit()

    response = client.delete(
        f"/api/users/{publisher_id}", headers=bearer_for(app, root_id, "superadmin")
    )
    assert response.status_code == 409
    assert response.json == {"error": "User is in use"}
