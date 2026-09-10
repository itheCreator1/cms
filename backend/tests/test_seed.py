from datetime import timedelta

import pytest
from flask_migrate import upgrade
from sqlalchemy import text


class SeedTestConfig:
    TESTING = True
    SECRET_KEY = "seed-test-secret"
    JWT_SECRET_KEY = "seed-jwt-test-secret-at-least-32-bytes"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FRONTEND_ORIGIN = "http://frontend.test"
    RATELIMIT_STORAGE_URI = "memory://"
    RATELIMIT_ENABLED = False


@pytest.fixture(scope="module")
def app(postgres_database_url):
    from backend.app import create_app

    SeedTestConfig.SQLALCHEMY_DATABASE_URI = postgres_database_url
    application = create_app(SeedTestConfig)
    with application.app_context():
        upgrade(directory="migrations")
    return application


@pytest.fixture(autouse=True)
def clean_database(app):
    from backend.extensions import db

    with app.app_context():
        db.session.execute(text("TRUNCATE TABLE users, categories CASCADE"))
        db.session.commit()
    yield
    with app.app_context():
        db.session.rollback()
        db.session.remove()


def test_seed_fails_clearly_without_superadmin_credentials(app):
    result = app.test_cli_runner().invoke(
        args=["seed"],
        env={"SEED_SUPERADMIN_EMAIL": "", "SEED_SUPERADMIN_PASSWORD": ""},
    )

    assert result.exit_code != 0
    assert "SEED_SUPERADMIN_EMAIL and SEED_SUPERADMIN_PASSWORD are required" in result.output


def test_seed_is_idempotent_and_safely_updates_matching_superadmin(app):
    from backend.extensions import db
    from backend.models import Category, User, UserRole

    runner = app.test_cli_runner()
    email = "root@example.test"
    first_password = "first seed password"
    second_password = "rotated seed password"

    first = runner.invoke(
        args=["seed"],
        env={
            "SEED_SUPERADMIN_EMAIL": f" {email.upper()} ",
            "SEED_SUPERADMIN_PASSWORD": first_password,
        },
    )
    assert first.exit_code == 0, first.output

    with app.app_context():
        first_user = db.session.execute(
            db.select(User).where(User.email == email)
        ).scalar_one()
        first_user_id = first_user.id
        assert first_user.role is UserRole.SUPERADMIN
        assert first_user.check_password(first_password)
        first_categories = db.session.execute(
            db.select(Category).order_by(Category.slug)
        ).scalars().all()
        first_category_ids = {category.slug: category.id for category in first_categories}
        assert len(first_category_ids) >= 3

    second = runner.invoke(
        args=["seed"],
        env={
            "SEED_SUPERADMIN_EMAIL": email,
            "SEED_SUPERADMIN_PASSWORD": second_password,
        },
    )
    assert second.exit_code == 0, second.output

    with app.app_context():
        users = db.session.execute(
            db.select(User).where(User.email == email)
        ).scalars().all()
        assert len(users) == 1
        assert users[0].id == first_user_id
        assert users[0].role is UserRole.SUPERADMIN
        assert users[0].check_password(second_password)
        assert not users[0].check_password(first_password)
        repeated_categories = db.session.execute(
            db.select(Category).order_by(Category.slug)
        ).scalars().all()
        assert {category.slug: category.id for category in repeated_categories} == first_category_ids

    combined_output = first.output + second.output
    assert email not in combined_output
    assert first_password not in combined_output
    assert second_password not in combined_output


def test_seed_promotes_existing_matching_account_without_creating_duplicate(app):
    from backend.extensions import db
    from backend.models import User, UserRole

    with app.app_context():
        existing = User(email="existing@example.test", role=UserRole.VISITOR)
        existing.set_password("old visitor password")
        db.session.add(existing)
        db.session.commit()
        existing_id = existing.id

    result = app.test_cli_runner().invoke(
        args=["seed"],
        env={
            "SEED_SUPERADMIN_EMAIL": "existing@example.test",
            "SEED_SUPERADMIN_PASSWORD": "new superadmin password",
        },
    )

    assert result.exit_code == 0, result.output
    with app.app_context():
        users = db.session.execute(db.select(User)).scalars().all()
        assert len(users) == 1
        assert users[0].id == existing_id
        assert users[0].role is UserRole.SUPERADMIN
        assert users[0].check_password("new superadmin password")
