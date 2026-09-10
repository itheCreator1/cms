import pytest
from sqlalchemy import UniqueConstraint, inspect
from sqlalchemy.exc import IntegrityError


def _column(model, name):
    return inspect(model).columns[name]


def _foreign_key(model, column_name):
    return next(iter(_column(model, column_name).foreign_keys))


def _relationship(model, name):
    return inspect(model).relationships[name]


def _unique_constraint_names(model):
    return {
        constraint.name
        for constraint in inspect(model).local_table.constraints
        if isinstance(constraint, UniqueConstraint)
    }


def _index_names(model):
    return {index.name for index in inspect(model).local_table.indexes}


def test_domain_model_metadata_matches_the_cms_contract():
    from backend import models

    expected_columns = {
        "User": {"id", "email", "password_hash", "role", "created_at"},
        "Article": {
            "id",
            "title",
            "slug",
            "body",
            "status",
            "author_id",
            "category_id",
            "featured_image_id",
            "created_at",
            "updated_at",
            "published_at",
        },
        "Announcement": {
            "id",
            "title",
            "body",
            "status",
            "author_id",
            "created_at",
            "published_at",
            "expires_at",
        },
        "Page": {
            "id",
            "title",
            "slug",
            "body",
            "status",
            "author_id",
            "updated_at",
        },
        "Category": {"id", "name", "slug"},
        "Tag": {"id", "name", "slug"},
        "Media": {
            "id",
            "filename",
            "url",
            "uploaded_by",
            "uploaded_at",
            "file_type",
            "source_type",
            "media_type",
            "provider",
            "storage_key",
            "alt_text",
        },
    }

    for model_name, column_names in expected_columns.items():
        model = getattr(models, model_name)
        assert set(inspect(model).columns.keys()) == column_names

    assert _column(models.User, "role").type.enums == [
        "visitor",
        "publisher",
        "admin",
        "superadmin",
    ]
    assert _column(models.User, "role").type.name == "user_role"
    assert _column(models.Article, "status").type.enums == [
        "draft",
        "pending_review",
        "published",
    ]
    assert _column(models.Article, "status").type.name == "article_status"
    assert _column(models.Announcement, "status").type.enums == [
        "draft",
        "pending_review",
        "published",
    ]
    assert _column(models.Announcement, "status").type.name == "announcement_status"
    assert _column(models.Page, "status").type.enums == ["draft", "published"]
    assert _column(models.Page, "status").type.name == "page_status"

    required_columns = {
        models.User: {"email", "password_hash", "role", "created_at"},
        models.Article: {
            "title",
            "slug",
            "body",
            "status",
            "author_id",
            "category_id",
            "created_at",
            "updated_at",
        },
        models.Announcement: {
            "title",
            "body",
            "status",
            "author_id",
            "created_at",
        },
        models.Page: {"title", "slug", "body", "status", "author_id", "updated_at"},
        models.Category: {"name", "slug"},
        models.Tag: {"name", "slug"},
        models.Media: {
            "filename",
            "url",
            "uploaded_by",
            "uploaded_at",
            "file_type",
            "source_type",
            "media_type",
        },
    }
    for model, names in required_columns.items():
        assert all(not _column(model, name).nullable for name in names)

    optional_columns = {
        models.Article: {"featured_image_id", "published_at"},
        models.Announcement: {"published_at", "expires_at"},
        models.Media: {"provider", "storage_key", "alt_text"},
    }
    for model, names in optional_columns.items():
        assert all(_column(model, name).nullable for name in names)

    expected_foreign_keys = {
        (models.Article, "author_id"): "users.id",
        (models.Article, "category_id"): "categories.id",
        (models.Article, "featured_image_id"): "media.id",
        (models.Announcement, "author_id"): "users.id",
        (models.Page, "author_id"): "users.id",
        (models.Media, "uploaded_by"): "users.id",
    }
    for (model, column_name), target in expected_foreign_keys.items():
        foreign_key = _foreign_key(model, column_name)
        assert foreign_key.target_fullname == target
        assert foreign_key.ondelete == "RESTRICT"

    assert _unique_constraint_names(models.User) == {"uq_users_email"}
    assert _unique_constraint_names(models.Article) == {"uq_articles_slug"}
    assert _unique_constraint_names(models.Page) == {"uq_pages_slug"}
    assert _unique_constraint_names(models.Category) == {
        "uq_categories_name",
        "uq_categories_slug",
    }
    assert _unique_constraint_names(models.Tag) == {
        "uq_tags_name",
        "uq_tags_slug",
    }
    assert _unique_constraint_names(models.Media) == {
        "uq_media_url",
        "uq_media_storage_key",
    }
    assert _index_names(models.Article) == {"ix_articles_slug"}
    assert _index_names(models.Page) == {"ix_pages_slug"}
    assert _index_names(models.Category) == {"ix_categories_slug"}
    assert _index_names(models.Tag) == {"ix_tags_slug"}

    assert set(models.article_tags.c.keys()) == {"article_id", "tag_id"}
    assert {foreign_key.target_fullname for foreign_key in models.article_tags.foreign_keys} == {
        "articles.id",
        "tags.id",
    }
    assert all(
        foreign_key.ondelete == "RESTRICT"
        for foreign_key in models.article_tags.foreign_keys
    )

    expected_relationships = {
        models.User: {"articles", "announcements", "pages", "media"},
        models.Article: {"author", "category", "featured_image", "tags"},
        models.Announcement: {"author"},
        models.Page: {"author"},
        models.Category: {"articles"},
        models.Tag: {"articles"},
        models.Media: {"uploader", "featured_articles"},
    }
    for model, names in expected_relationships.items():
        assert set(inspect(model).relationships.keys()) == names
        for relationship_name in names:
            cascade = _relationship(model, relationship_name).cascade
            assert "delete" not in cascade
            assert "delete-orphan" not in cascade


def test_user_hashes_passwords_and_checks_credentials_without_storing_plaintext():
    from backend.models import User

    user = User(email="publisher@example.test")

    user.set_password("correct horse battery staple")

    assert user.password_hash != "correct horse battery staple"
    assert "correct horse battery staple" not in user.password_hash
    assert user.check_password("correct horse battery staple")
    assert not user.check_password("wrong password")


@pytest.fixture()
def postgres_session(postgres_database_url):
    from flask_migrate import upgrade

    from backend.app import create_app
    from backend.extensions import db

    class PostgreSQLTestConfig:
        TESTING = True
        SECRET_KEY = "model-test-only"
        SQLALCHEMY_DATABASE_URI = postgres_database_url
        SQLALCHEMY_TRACK_MODIFICATIONS = False
        FRONTEND_ORIGIN = "http://frontend.test"

    application = create_app(PostgreSQLTestConfig)
    with application.app_context():
        assert db.engine.dialect.name == "postgresql"
        upgrade(directory="migrations")
        yield db.session
        db.session.rollback()
        db.session.remove()


def test_domain_models_persist_relationships_and_defaults_in_postgresql(
    postgres_session,
):
    from backend.models import (
        Announcement,
        AnnouncementStatus,
        Article,
        ArticleStatus,
        Category,
        Media,
        Page,
        PageStatus,
        Tag,
        User,
        UserRole,
    )

    author = User(email="author@example.test")
    author.set_password("a strong password")
    category = Category(name="News", slug="news")
    tag = Tag(name="Local", slug="local")
    image = Media(
        filename="front-page.jpg",
        url="/media/front-page.jpg",
        uploader=author,
        file_type="image/jpeg",
        source_type="upload",
        media_type="image",
        provider="local",
        storage_key="front-page.jpg",
        alt_text="Front page",
    )
    article = Article(
        title="Front page",
        slug="front-page",
        body="Article body",
        author=author,
        category=category,
        featured_image=image,
        tags=[tag],
    )
    announcement = Announcement(
        title="Office hours",
        body="Updated hours",
        author=author,
    )
    page = Page(
        title="About",
        slug="about",
        body="About this site",
        author=author,
    )
    postgres_session.add_all([article, announcement, page])
    postgres_session.flush()

    assert author.role is UserRole.VISITOR
    assert article.status is ArticleStatus.DRAFT
    assert announcement.status is AnnouncementStatus.DRAFT
    assert page.status is PageStatus.DRAFT
    assert article in author.articles
    assert announcement in author.announcements
    assert page in author.pages
    assert image in author.media
    assert article.category is category
    assert article.featured_image is image
    assert article.tags == [tag]
    assert article in tag.articles
    assert article.created_at.tzinfo is not None
    assert article.updated_at.tzinfo is not None
    assert announcement.created_at.tzinfo is not None
    assert image.uploaded_at.tzinfo is not None
    assert image.source_type == "upload"
    assert image.media_type == "image"
    assert image.provider == "local"
    assert image.alt_text == "Front page"


def test_postgresql_enforces_unique_email(postgres_session):
    from backend.models import User

    first = User(email="duplicate@example.test")
    first.set_password("first password")
    duplicate = User(email="duplicate@example.test")
    duplicate.set_password("second password")
    postgres_session.add_all([first, duplicate])

    with pytest.raises(IntegrityError) as error:
        postgres_session.flush()

    assert error.value.orig.diag.constraint_name == "uq_users_email"


def test_postgresql_restricts_deleting_referenced_authors(postgres_session):
    from sqlalchemy import delete

    from backend.models import Article, Category, User

    author = User(email="referenced@example.test")
    author.set_password("a strong password")
    article = Article(
        title="Retained article",
        slug="retained-article",
        body="Must not be silently deleted",
        author=author,
        category=Category(name="Required category", slug="required-category"),
    )
    postgres_session.add(article)
    postgres_session.flush()

    with pytest.raises(IntegrityError) as error:
        postgres_session.execute(delete(User).where(User.id == author.id))

    assert error.value.orig.diag.constraint_name == "fk_articles_author_id_users"
