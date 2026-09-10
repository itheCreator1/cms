from enum import Enum

from backend.extensions import db


class ArticleStatus(str, Enum):
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    PUBLISHED = "published"


article_tags = db.Table(
    "article_tags",
    db.Column(
        "article_id",
        db.Integer,
        db.ForeignKey("articles.id", ondelete="RESTRICT"),
        primary_key=True,
    ),
    db.Column(
        "tag_id",
        db.Integer,
        db.ForeignKey("tags.id", ondelete="RESTRICT"),
        primary_key=True,
    ),
)


class Article(db.Model):
    __tablename__ = "articles"
    __table_args__ = (
        db.UniqueConstraint("slug", name="uq_articles_slug"),
        db.Index("ix_articles_slug", "slug"),
    )

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), nullable=False)
    body = db.Column(db.Text, nullable=False)
    status = db.Column(
        db.Enum(
            ArticleStatus,
            name="article_status",
            values_callable=lambda enum: [member.value for member in enum],
            validate_strings=True,
        ),
        nullable=False,
        default=ArticleStatus.DRAFT,
        server_default=ArticleStatus.DRAFT.value,
    )
    author_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    category_id = db.Column(
        db.Integer,
        db.ForeignKey("categories.id", ondelete="RESTRICT"),
        nullable=False,
    )
    featured_image_id = db.Column(
        db.Integer,
        db.ForeignKey("media.id", ondelete="RESTRICT"),
        nullable=True,
    )
    created_at = db.Column(
        db.DateTime(timezone=True), nullable=False, server_default=db.func.now()
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        server_default=db.func.now(),
        onupdate=db.func.now(),
    )
    published_at = db.Column(db.DateTime(timezone=True), nullable=True)

    author = db.relationship("User", back_populates="articles")
    category = db.relationship("Category", back_populates="articles")
    featured_image = db.relationship("Media", back_populates="featured_articles")
    tags = db.relationship("Tag", secondary=article_tags, back_populates="articles")
