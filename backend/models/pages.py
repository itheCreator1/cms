from enum import Enum

from backend.extensions import db


class PageStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"


class Page(db.Model):
    __tablename__ = "pages"
    __table_args__ = (
        db.UniqueConstraint("slug", name="uq_pages_slug"),
        db.Index("ix_pages_slug", "slug"),
    )

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), nullable=False)
    body = db.Column(db.Text, nullable=False)
    status = db.Column(
        db.Enum(
            PageStatus,
            name="page_status",
            values_callable=lambda enum: [member.value for member in enum],
            validate_strings=True,
        ),
        nullable=False,
        default=PageStatus.DRAFT,
        server_default=PageStatus.DRAFT.value,
    )
    author_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        server_default=db.func.now(),
        onupdate=db.func.now(),
    )

    author = db.relationship("User", back_populates="pages")
