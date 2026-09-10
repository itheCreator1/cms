import pytest
from sqlalchemy import inspect, text


@pytest.fixture()
def postgres_app(postgres_database_url):
    from backend.app import create_app
    from backend.extensions import db

    class PostgreSQLTestConfig:
        TESTING = True
        SECRET_KEY = "migration-test-only"
        SQLALCHEMY_DATABASE_URI = postgres_database_url
        SQLALCHEMY_TRACK_MODIFICATIONS = False
        FRONTEND_ORIGIN = "http://frontend.test"

    application = create_app(PostgreSQLTestConfig)
    with application.app_context():
        assert db.engine.dialect.name == "postgresql"
        yield application
        db.session.remove()


def _enum_names(connection):
    return set(
        connection.execute(
            text(
                "SELECT typname FROM pg_type "
                "WHERE typname IN "
                "('user_role', 'article_status', 'announcement_status', 'page_status')"
            )
        ).scalars()
    )


def test_first_revision_round_trips_the_postgresql_domain_schema(postgres_app):
    from flask_migrate import downgrade, upgrade

    from backend.extensions import db

    expected_tables = {
        "users",
        "articles",
        "announcements",
        "pages",
        "categories",
        "tags",
        "media",
        "article_tags",
    }
    expected_enum_names = {
        "user_role",
        "article_status",
        "announcement_status",
        "page_status",
    }

    try:
        downgrade(directory="migrations", revision="base")
        upgrade(directory="migrations")

        inspector = inspect(db.engine)
        assert expected_tables <= set(inspector.get_table_names())
        assert {item["name"] for item in inspector.get_unique_constraints("users")} == {
            "uq_users_email"
        }
        assert {item["name"] for item in inspector.get_unique_constraints("categories")} == {
            "uq_categories_name",
            "uq_categories_slug",
        }
        assert {item["name"] for item in inspector.get_unique_constraints("tags")} == {
            "uq_tags_name",
            "uq_tags_slug",
        }
        assert {item["name"] for item in inspector.get_unique_constraints("media")} == {
            "uq_media_url"
        }
        assert "ix_articles_slug" in {
            item["name"] for item in inspector.get_indexes("articles")
        }
        assert "ix_pages_slug" in {
            item["name"] for item in inspector.get_indexes("pages")
        }
        assert "ix_categories_slug" in {
            item["name"] for item in inspector.get_indexes("categories")
        }
        assert "ix_tags_slug" in {
            item["name"] for item in inspector.get_indexes("tags")
        }
        article_columns = {
            item["name"]: item for item in inspector.get_columns("articles")
        }
        assert not article_columns["category_id"]["nullable"]
        assert article_columns["featured_image_id"]["nullable"]
        assert article_columns["published_at"]["nullable"]
        with db.engine.connect() as connection:
            assert _enum_names(connection) == expected_enum_names

        db.session.remove()
        downgrade(directory="migrations", revision="base")

        inspector = inspect(db.engine)
        assert expected_tables.isdisjoint(inspector.get_table_names())
        with db.engine.connect() as connection:
            assert _enum_names(connection) == set()
    finally:
        db.session.remove()
        upgrade(directory="migrations")

    assert expected_tables <= set(inspect(db.engine).get_table_names())
