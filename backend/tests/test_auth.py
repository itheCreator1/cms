from datetime import timedelta
from io import StringIO
import re

import pytest
from flask import jsonify
from flask_migrate import upgrade
from sqlalchemy import text


class AuthTestConfig:
    TESTING = True
    SECRET_KEY = "auth-test-secret"
    JWT_SECRET_KEY = "jwt-test-secret-at-least-32-bytes-long"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
    JWT_TOKEN_LOCATION = ["headers"]
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FRONTEND_ORIGIN = "http://frontend.test"
    RATELIMIT_STORAGE_URI = "memory://"
    RATELIMIT_ENABLED = True


@pytest.fixture(scope="module")
def app(postgres_database_url):
    from backend.app import create_app
    from backend.utils.auth_helpers import role_required

    AuthTestConfig.SQLALCHEMY_DATABASE_URI = postgres_database_url
    application = create_app(AuthTestConfig)

    @application.get("/api/publisher-area")
    @role_required("publisher")
    def publisher_area():
        return jsonify(ok=True)

    @application.get("/api/admin-area")
    @role_required("admin")
    def admin_area():
        return jsonify(ok=True)

    @application.get("/api/superadmin-area")
    @role_required("superadmin")
    def superadmin_area():
        return jsonify(ok=True)

    with application.app_context():
        upgrade(directory="migrations")

    return application


@pytest.fixture(autouse=True)
def clean_database(app):
    from backend.extensions import db

    with app.app_context():
        db.session.execute(text("TRUNCATE TABLE users, categories CASCADE"))
        db.session.commit()
    for app_limiter in app.extensions.get("limiter", set()):
        app_limiter.reset()

    yield

    with app.app_context():
        db.session.rollback()
        db.session.remove()


@pytest.fixture()
def client(app):
    return app.test_client()


def create_user(app, email, password="correct horse battery staple", role="visitor"):
    from backend.extensions import db
    from backend.models import User, UserRole

    with app.app_context():
        user = User(email=email, role=UserRole(role))
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user.id


def bearer(token):
    return {"Authorization": f"Bearer {token}"}


def test_signup_normalizes_email_hashes_password_and_returns_only_public_identity(
    app, client
):
    from backend.extensions import db
    from backend.models import User, UserRole

    response = client.post(
        "/api/signup",
        json={
            "email": "  New.Visitor@Example.TEST  ",
            "password": "correct horse battery staple",
        },
    )

    assert response.status_code == 201
    assert set(response.json) == {"user"}
    assert set(response.json["user"]) == {"id", "email", "role", "created_at"}
    assert response.json["user"]["email"] == "new.visitor@example.test"
    assert response.json["user"]["role"] == "visitor"
    assert "password" not in response.get_data(as_text=True).lower()
    assert "token" not in response.get_data(as_text=True).lower()

    with app.app_context():
        user = db.session.execute(
            db.select(User).where(User.email == "new.visitor@example.test")
        ).scalar_one()
        assert user.role is UserRole.VISITOR
        assert user.password_hash != "correct horse battery staple"
        assert user.check_password("correct horse battery staple")


@pytest.mark.parametrize(
    "payload",
    [
        None,
        {},
        {"email": "not-an-email", "password": "correct horse battery staple"},
        {"email": "person@example.test", "password": "short"},
        {"email": 12, "password": "correct horse battery staple"},
    ],
)
def test_signup_rejects_invalid_json_credentials(client, payload):
    response = client.post("/api/signup", json=payload)

    assert response.status_code == 400
    assert response.content_type == "application/json"
    assert response.json == {"error": "Invalid signup data"}


def test_signup_rejects_duplicate_normalized_email_with_json_conflict(client):
    payload = {
        "email": "visitor@example.test",
        "password": "correct horse battery staple",
    }
    assert client.post("/api/signup", json=payload).status_code == 201

    response = client.post(
        "/api/signup",
        json={**payload, "email": " Visitor@Example.TEST "},
    )

    assert response.status_code == 409
    assert response.content_type == "application/json"
    assert response.json == {"error": "Email is already registered"}


def test_signup_rejects_non_json_requests_with_json_error(client):
    response = client.post(
        "/api/signup", data="email=x", content_type="application/x-www-form-urlencoded"
    )

    assert response.status_code == 400
    assert response.content_type == "application/json"
    assert response.json == {"error": "Invalid signup data"}


@pytest.mark.parametrize(
    "email",
    [
        f"{'a' * 244}@example.test",
        "control\x00@example.test",
        "control\n@example.test",
    ],
)
@pytest.mark.parametrize(
    "endpoint,error_message",
    [
        ("/api/signup", "Invalid signup data"),
        ("/api/login", "Invalid login data"),
        ("/api/superadmin-login", "Invalid login data"),
    ],
)
def test_auth_endpoints_reject_overlong_or_control_email_as_safe_json(
    client, endpoint, error_message, email
):
    response = client.post(
        endpoint,
        json={"email": email, "password": "correct horse battery staple"},
    )

    assert response.status_code == 400
    assert response.content_type == "application/json"
    assert response.json == {"error": error_message}
    assert email not in response.get_data(as_text=True)


@pytest.mark.parametrize("role", ["visitor", "publisher", "admin"])
def test_regular_login_returns_bearer_jwt_with_string_identity_and_role_claim(
    app, client, role
):
    from flask_jwt_extended import decode_token

    user_id = create_user(app, f"{role}@example.test", role=role)

    response = client.post(
        "/api/login",
        json={
            "email": f" {role.upper()}@EXAMPLE.TEST ",
            "password": "correct horse battery staple",
        },
    )

    assert response.status_code == 200
    assert set(response.json) == {"access_token", "user"}
    assert response.json["user"]["role"] == role
    assert "password" not in response.get_data(as_text=True).lower()
    with app.app_context():
        decoded = decode_token(response.json["access_token"])
    assert decoded["sub"] == str(user_id)
    assert decoded["role"] == role
    assert decoded["auth_channel"] == "regular"

    me = client.get("/api/me", headers=bearer(response.json["access_token"]))
    assert me.status_code == 200
    assert me.json == {"user": response.json["user"]}


@pytest.mark.parametrize(
    "email,password,stored_role",
    [
        ("unknown@example.test", "correct horse battery staple", None),
        ("known@example.test", "wrong horse battery staple", "visitor"),
        ("known@example.test", "correct horse battery staple", "superadmin"),
    ],
)
def test_regular_login_uses_one_generic_error_for_all_denied_credentials(
    app, client, email, password, stored_role
):
    if stored_role:
        create_user(app, "known@example.test", role=stored_role)

    response = client.post(
        "/api/login", json={"email": email, "password": password}
    )

    assert response.status_code == 401
    assert response.content_type == "application/json"
    assert response.json == {"error": "Invalid credentials"}


def test_regular_login_rejects_invalid_request_as_json(client):
    response = client.post("/api/login", json={"email": "missing-password@example.test"})

    assert response.status_code == 400
    assert response.json == {"error": "Invalid login data"}


def test_superadmin_login_succeeds_only_for_superadmin(app, client):
    from flask_jwt_extended import decode_token

    create_user(app, "root@example.test", role="superadmin")

    response = client.post(
        "/api/superadmin-login",
        json={
            "email": "root@example.test",
            "password": "correct horse battery staple",
        },
        environ_base={"REMOTE_ADDR": "192.0.2.10"},
    )

    assert response.status_code == 200
    assert response.json["user"]["role"] == "superadmin"
    assert response.json["access_token"]
    with app.app_context():
        decoded = decode_token(response.json["access_token"])
    assert decoded["auth_channel"] == "superadmin"


@pytest.mark.parametrize(
    "email,password,stored_role",
    [
        ("unknown@example.test", "correct horse battery staple", None),
        ("root@example.test", "wrong horse battery staple", "superadmin"),
        ("admin@example.test", "correct horse battery staple", "admin"),
    ],
)
def test_superadmin_login_uses_one_generic_error_for_every_denial(
    app, client, email, password, stored_role
):
    if stored_role:
        create_user(app, email, role=stored_role)

    response = client.post(
        "/api/superadmin-login",
        json={"email": email, "password": password},
        environ_base={"REMOTE_ADDR": "192.0.2.11"},
    )

    assert response.status_code == 401
    assert response.json == {"error": "Invalid credentials"}


def test_superadmin_login_verifies_found_password_before_role_rejection(
    app, client, monkeypatch
):
    from backend.models import User, UserRole

    create_user(app, "admin@example.test", role="admin")
    checked_roles = []
    real_check_password = User.check_password

    def record_check(user, password):
        checked_roles.append(user.role)
        return real_check_password(user, password)

    monkeypatch.setattr(User, "check_password", record_check)

    response = client.post(
        "/api/superadmin-login",
        json={
            "email": "admin@example.test",
            "password": "correct horse battery staple",
        },
    )

    assert response.status_code == 401
    assert checked_roles == [UserRole.ADMIN]


def test_superadmin_login_logs_timestamp_ip_and_outcome_without_credentials_or_token(
    app, client, monkeypatch
):
    from backend.extensions import db
    from backend.models import User
    from backend.utils.security_logging import security_logger

    password = "log sanitization password"
    create_user(app, "private@example.test", password=password, role="superadmin")
    with app.app_context():
        password_hash = db.session.execute(
            db.select(User.password_hash).where(User.email == "private@example.test")
        ).scalar_one()

    log_output = StringIO()
    handler = next(
        handler
        for handler in security_logger.handlers
        if getattr(handler, "_cms_auth_handler", False)
    )
    monkeypatch.setattr(handler, "stream", log_output)

    response = client.post(
        "/api/superadmin-login",
        json={"email": "private@example.test", "password": password},
        environ_base={"REMOTE_ADDR": "198.51.100.24"},
    )
    captured = log_output.getvalue()

    assert response.status_code == 200
    assert "198.51.100.24" in captured
    assert re.search(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", captured)
    assert "outcome=success" in captured
    assert "superadmin_login" in captured
    assert "private@example.test" not in captured
    assert password not in captured
    assert password_hash not in captured
    assert response.json["access_token"] not in captured


def test_denied_malformed_and_rate_limited_superadmin_attempts_are_all_safely_logged(
    app, client, monkeypatch
):
    from backend.extensions import db
    from backend.models import User
    from backend.utils.security_logging import security_logger

    denied_email = "denied-admin@example.test"
    denied_password = "denied admin password"
    create_user(app, denied_email, password=denied_password, role="admin")
    with app.app_context():
        denied_hash = db.session.execute(
            db.select(User.password_hash).where(User.email == denied_email)
        ).scalar_one()

    log_output = StringIO()
    handler = next(
        handler
        for handler in security_logger.handlers
        if getattr(handler, "_cms_auth_handler", False)
    )
    monkeypatch.setattr(handler, "stream", log_output)

    denied = client.post(
        "/api/superadmin-login",
        json={"email": denied_email, "password": denied_password},
        environ_base={"REMOTE_ADDR": "198.51.100.30"},
    )
    malformed = client.post(
        "/api/superadmin-login",
        json={"email": "missing-password@example.test"},
        environ_base={"REMOTE_ADDR": "198.51.100.31"},
    )
    rate_responses = [
        client.post(
            "/api/superadmin-login",
            json={
                "email": "unknown@example.test",
                "password": "unknown account password",
            },
            environ_base={"REMOTE_ADDR": "198.51.100.32"},
        )
        for _attempt in range(6)
    ]
    captured = log_output.getvalue()

    assert denied.status_code == 401
    assert malformed.status_code == 400
    assert [response.status_code for response in rate_responses] == [
        401,
        401,
        401,
        401,
        401,
        429,
    ]
    assert captured.count("ip=198.51.100.30 outcome=failure") == 1
    assert captured.count("ip=198.51.100.31 outcome=failure") == 1
    assert captured.count("ip=198.51.100.32 outcome=failure") == 6
    assert denied_email not in captured
    assert denied_password not in captured
    assert denied_hash not in captured
    assert "missing-password@example.test" not in captured
    assert "unknown@example.test" not in captured


def test_regular_login_is_limited_to_twenty_attempts_per_remote_ip(client):
    for attempt in range(20):
        response = client.post(
            "/api/login",
            json={"email": "unknown@example.test", "password": f"wrong-password-{attempt}"},
            environ_base={"REMOTE_ADDR": "203.0.113.20"},
        )
        assert response.status_code == 401

    exceeded = client.post(
        "/api/login",
        json={"email": "unknown@example.test", "password": "one-too-many-password"},
        environ_base={"REMOTE_ADDR": "203.0.113.20"},
    )

    assert exceeded.status_code == 429
    assert exceeded.content_type == "application/json"
    assert exceeded.json == {"error": "Rate limit exceeded"}


def test_superadmin_login_is_limited_to_five_attempts_and_ignores_forwarded_ip(
    client,
):
    for attempt in range(5):
        response = client.post(
            "/api/superadmin-login",
            json={"email": "unknown@example.test", "password": "wrong password value"},
            headers={"X-Forwarded-For": f"10.0.0.{attempt}"},
            environ_base={"REMOTE_ADDR": "203.0.113.5"},
        )
        assert response.status_code == 401

    exceeded = client.post(
        "/api/superadmin-login",
        json={"email": "unknown@example.test", "password": "wrong password value"},
        headers={"X-Forwarded-For": "10.0.0.200"},
        environ_base={"REMOTE_ADDR": "203.0.113.5"},
    )

    assert exceeded.status_code == 429
    assert exceeded.json == {"error": "Rate limit exceeded"}


def make_token(app, identity, role="visitor", expires_delta=None):
    from flask_jwt_extended import create_access_token

    with app.app_context():
        return create_access_token(
            identity=identity,
            additional_claims={
                "role": role,
                "auth_channel": "superadmin" if role == "superadmin" else "regular",
            },
            expires_delta=expires_delta,
        )


@pytest.mark.parametrize(
    "headers",
    [
        {},
        {"Authorization": "Bearer not-a-jwt"},
    ],
)
def test_me_returns_same_json_401_for_missing_or_invalid_bearer_token(client, headers):
    response = client.get("/api/me", headers=headers)

    assert response.status_code == 401
    assert response.content_type == "application/json"
    assert response.json == {"error": "Authentication required"}


def test_me_rejects_expired_token_with_same_json_401(app, client):
    user_id = create_user(app, "expired@example.test")
    token = make_token(
        app,
        str(user_id),
        expires_delta=timedelta(seconds=-1),
    )

    response = client.get("/api/me", headers=bearer(token))

    assert response.status_code == 401
    assert response.json == {"error": "Authentication required"}


@pytest.mark.parametrize("identity", ["not-a-number", "99999999"])
def test_me_rejects_malformed_or_unknown_string_identity(app, client, identity):
    token = make_token(app, identity)

    response = client.get("/api/me", headers=bearer(token))

    assert response.status_code == 401
    assert response.json == {"error": "Authentication required"}


def test_me_rejects_token_after_authenticated_user_is_deleted(app, client):
    from backend.extensions import db
    from backend.models import User

    user_id = create_user(app, "deleted@example.test")
    token = make_token(app, str(user_id))
    with app.app_context():
        user = db.session.get(User, user_id)
        db.session.delete(user)
        db.session.commit()

    response = client.get("/api/me", headers=bearer(token))

    assert response.status_code == 401
    assert response.json == {"error": "Authentication required"}


@pytest.mark.parametrize(
    "role,expected_status",
    [
        ("visitor", 403),
        ("publisher", 200),
        ("admin", 200),
        ("superadmin", 200),
    ],
)
def test_role_required_uses_numeric_inheritance_and_denial_boundary(
    app, client, role, expected_status
):
    user_id = create_user(app, f"role-{role}@example.test", role=role)
    token = make_token(app, str(user_id), role=role)

    response = client.get("/api/publisher-area", headers=bearer(token))

    assert response.status_code == expected_status
    if expected_status == 200:
        assert response.json == {"ok": True}
    else:
        assert response.json == {"error": "Insufficient permissions"}


def test_role_required_rejects_unknown_role_configuration():
    from backend.utils.auth_helpers import role_required

    with pytest.raises(ValueError, match="Unknown role"):
        role_required("editor")


@pytest.mark.parametrize(
    "endpoint,role,expected_status",
    [
        ("/api/admin-area", "publisher", 403),
        ("/api/admin-area", "admin", 200),
        ("/api/admin-area", "superadmin", 200),
        ("/api/superadmin-area", "admin", 403),
        ("/api/superadmin-area", "superadmin", 200),
    ],
)
def test_admin_and_superadmin_role_denial_boundaries(
    app, client, endpoint, role, expected_status
):
    user_id = create_user(app, f"boundary-{role}@example.test", role=role)
    token = make_token(app, str(user_id), role=role)

    response = client.get(endpoint, headers=bearer(token))

    assert response.status_code == expected_status
    if expected_status == 403:
        assert response.json == {"error": "Insufficient permissions"}
    else:
        assert response.json == {"ok": True}


@pytest.mark.parametrize(
    "token_role,current_role,expected_status",
    [
        ("admin", "visitor", 403),
        ("visitor", "publisher", 200),
    ],
)
def test_role_authorization_uses_current_database_role_not_stale_token_claim(
    app, client, token_role, current_role, expected_status
):
    from backend.extensions import db
    from backend.models import User, UserRole

    user_id = create_user(app, f"stale-{token_role}@example.test", role=token_role)
    token = make_token(app, str(user_id), role=token_role)
    with app.app_context():
        user = db.session.get(User, user_id)
        user.role = UserRole(current_role)
        db.session.commit()

    response = client.get("/api/publisher-area", headers=bearer(token))

    assert response.status_code == expected_status


def test_regular_token_cannot_become_superadmin_session_after_promotion(app, client):
    from backend.extensions import db
    from backend.models import User, UserRole

    user_id = create_user(app, "promoted@example.test", role="admin")
    token = make_token(app, str(user_id), role="admin")
    with app.app_context():
        db.session.get(User, user_id).role = UserRole.SUPERADMIN
        db.session.commit()

    response = client.get("/api/me", headers=bearer(token))

    assert response.status_code == 401
    assert response.json == {"error": "Authentication required"}


def test_limiter_enabled_state_is_isolated_between_application_instances(
    postgres_database_url,
):
    from backend.app import create_app

    class DisabledConfig(AuthTestConfig):
        SQLALCHEMY_DATABASE_URI = postgres_database_url
        RATELIMIT_ENABLED = False

    class DefaultEnabledConfig:
        TESTING = True
        SECRET_KEY = "limiter-isolation-test-secret"
        JWT_SECRET_KEY = "limiter-isolation-jwt-secret-over-32-bytes"
        JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
        JWT_TOKEN_LOCATION = ["headers"]
        SQLALCHEMY_DATABASE_URI = postgres_database_url
        SQLALCHEMY_TRACK_MODIFICATIONS = False
        FRONTEND_ORIGIN = "http://frontend.test"
        RATELIMIT_STORAGE_URI = "memory://"

    disabled_app = create_app(DisabledConfig)
    disabled_client = disabled_app.test_client()
    disabled_statuses = [
        disabled_client.post(
            "/api/login",
            json={"email": "unknown@example.test", "password": "wrong password value"},
            environ_base={"REMOTE_ADDR": "203.0.113.80"},
        ).status_code
        for _attempt in range(21)
    ]

    enabled_app = create_app(DefaultEnabledConfig)
    enabled_client = enabled_app.test_client()
    enabled_statuses = [
        enabled_client.post(
            "/api/login",
            json={"email": "unknown@example.test", "password": "wrong password value"},
            environ_base={"REMOTE_ADDR": "203.0.113.81"},
        ).status_code
        for _attempt in range(21)
    ]
    disabled_after_enabled_statuses = [
        disabled_client.post(
            "/api/login",
            json={"email": "unknown@example.test", "password": "wrong password value"},
            environ_base={"REMOTE_ADDR": "203.0.113.82"},
        ).status_code
        for _attempt in range(21)
    ]

    assert disabled_statuses == [401] * 21
    assert disabled_app.config["RATELIMIT_ENABLED"] is False
    assert enabled_app.config["RATELIMIT_ENABLED"] is True
    assert enabled_statuses == [401] * 20 + [429]
    assert disabled_after_enabled_statuses == [401] * 21
