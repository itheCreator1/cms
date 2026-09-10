from backend.extensions import db


class Tag(db.Model):
    __tablename__ = "tags"
    __table_args__ = (
        db.UniqueConstraint("name", name="uq_tags_name"),
        db.UniqueConstraint("slug", name="uq_tags_slug"),
        db.Index("ix_tags_slug", "slug"),
    )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), nullable=False)

    articles = db.relationship(
        "Article", secondary="article_tags", back_populates="tags"
    )
