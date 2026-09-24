import pytest
from flask_jwt_extended import create_access_token
from flask_migrate import upgrade
from sqlalchemy import text


class SettingsConfig:
    TESTING = True
    SECRET_KEY = "settings-test-secret"
    JWT_SECRET_KEY = "settings-jwt-test-secret-at-least-32-bytes"
    JWT_TOKEN_LOCATION = ["headers"]
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FRONTEND_ORIGIN = "http://frontend.test"
    RATELIMIT_ENABLED = False


@pytest.fixture(scope="module")
def app(postgres_database_url):
    from backend.app import create_app

    SettingsConfig.SQLALCHEMY_DATABASE_URI = postgres_database_url
    application = create_app(SettingsConfig)
    with application.app_context():
        upgrade(directory="migrations")
    return application


@pytest.fixture(autouse=True)
def clean_database(app):
    from backend.extensions import db

    with app.app_context():
        db.session.execute(text("TRUNCATE TABLE site_settings_changes, users RESTART IDENTITY CASCADE"))
        db.session.execute(text("UPDATE site_settings SET site_name = 'CMS', tagline = 'The daily edition', homepage_headline = 'Stories that keep us connected.', homepage_intro = 'News, notices, and voices from across the community.' WHERE id = 1"))
        db.session.commit()
    yield


def token(app, role):
    from backend.extensions import db
    from backend.models import User, UserRole

    with app.app_context():
        user = User(email=f"{role}@example.test", role=UserRole(role))
        user.set_password("test password")
        db.session.add(user)
        db.session.commit()
        auth = "superadmin" if role == "superadmin" else "regular"
        jwt = create_access_token(identity=str(user.id), additional_claims={"role": role, "auth_channel": auth})
        return {"Authorization": f"Bearer {jwt}"}, user.id


def test_public_defaults_and_superadmin_update_are_persistent_and_audited(app):
    client = app.test_client()
    expected = {
        "site_name": "CMS", "tagline": "The daily edition",
        "homepage_headline": "Stories that keep us connected.",
        "homepage_intro": "News, notices, and voices from across the community.",
    }
    assert client.get("/api/settings").json == {"item": expected}
    headers, actor_id = token(app, "superadmin")
    updated = {**expected, "site_name": "Community News", "homepage_intro": "Local updates."}
    response = client.put("/api/settings", headers=headers, json=updated)
    assert response.status_code == 200
    assert response.json == {"item": updated}
    assert client.get("/api/settings").json == {"item": updated}
    with app.app_context():
        from backend.extensions import db

        row = db.session.execute(text("SELECT actor_id, before_values, after_values, changed_at FROM site_settings_changes")).one()
        assert row.actor_id == actor_id
        assert row.before_values == expected
        assert row.after_values == updated
        assert row.changed_at is not None


@pytest.mark.parametrize("role", [None, "visitor", "publisher", "admin"])
def test_only_superadmin_can_update(app, role):
    headers = token(app, role)[0] if role else {}
    response = app.test_client().put("/api/settings", headers=headers, json={"site_name": "Forbidden"})
    assert response.status_code == (401 if role is None else 403)
    assert set(response.json) == {"error"}


@pytest.mark.parametrize("payload", [{}, {"site_name": ""}, {"site_name": "x" * 121}, {"unknown": "x"}, {"homepage_intro": 4}])
def test_invalid_settings_are_rejected_without_audit(app, payload):
    headers, _ = token(app, "superadmin")
    response = app.test_client().put("/api/settings", headers=headers, json=payload)
    assert response.status_code == 400
    assert set(response.json) == {"error"}
    with app.app_context():
        from backend.extensions import db

        assert db.session.scalar(text("SELECT count(*) FROM site_settings_changes")) == 0
