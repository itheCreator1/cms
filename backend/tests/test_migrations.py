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


def _enum_values(connection, enum_name):
    return list(
        connection.execute(
            text(
                "SELECT enumlabel FROM pg_enum "
                "JOIN pg_type ON pg_type.oid = pg_enum.enumtypid "
                "WHERE typname = :enum_name ORDER BY enumsortorder"
            ),
            {"enum_name": enum_name},
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
            "uq_media_url",
            "uq_media_storage_key",
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
            assert _enum_values(connection, "announcement_status") == [
                "draft",
                "pending_review",
                "published",
            ]

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


def test_media_asset_revision_preserves_existing_rows_and_downgrades(postgres_app):
    from flask_migrate import downgrade, upgrade

    from backend.extensions import db

    try:
        upgrade(directory="migrations", revision="5e2d9a6b1c44")
        with db.engine.begin() as connection:
            user_id = connection.execute(
                text(
                    "INSERT INTO users (email, password_hash, role) "
                    "VALUES ('legacy@example.test', 'hash', 'admin') RETURNING id"
                )
            ).scalar_one()
            connection.execute(
                text(
                    "INSERT INTO media (filename, url, uploaded_by, file_type) "
                    "VALUES ('legacy.jpg', '/legacy.jpg', :user_id, 'image/jpeg')"
                ),
                {"user_id": user_id},
            )

        upgrade(directory="migrations")
        columns = {
            column["name"]: column for column in inspect(db.engine).get_columns("media")
        }
        assert {"source_type", "media_type", "provider", "storage_key", "alt_text"} <= set(columns)
        assert not columns["source_type"]["nullable"]
        assert not columns["media_type"]["nullable"]
        with db.engine.begin() as connection:
            legacy = connection.execute(
                text(
                    "SELECT source_type, media_type, provider, storage_key, alt_text "
                    "FROM media WHERE url = '/legacy.jpg'"
                )
            ).mappings().one()
            assert dict(legacy) == {
                "source_type": "upload",
                "media_type": "image",
                "provider": None,
                "storage_key": None,
                "alt_text": None,
            }
            connection.execute(
                text(
                    "INSERT INTO media "
                    "(filename, url, uploaded_by, file_type, source_type, media_type, provider) "
                    "VALUES ('youtube.com', 'https://youtube.com/watch?v=1', :user_id, "
                    "'text/uri-list', 'external', 'video', 'youtube')"
                ),
                {"user_id": user_id},
            )

        downgrade(directory="migrations", revision="5e2d9a6b1c44")
        column_names = {
            column["name"] for column in inspect(db.engine).get_columns("media")
        }
        assert not {
            "source_type",
            "media_type",
            "provider",
            "storage_key",
            "alt_text",
        } & column_names
        with db.engine.connect() as connection:
            assert connection.execute(text("SELECT count(*) FROM media")).scalar_one() == 2
    finally:
        db.session.remove()
        upgrade(directory="migrations")
