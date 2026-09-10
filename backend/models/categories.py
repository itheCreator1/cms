from backend.extensions import db


class Category(db.Model):
    __tablename__ = "categories"
    __table_args__ = (
        db.UniqueConstraint("name", name="uq_categories_name"),
        db.UniqueConstraint("slug", name="uq_categories_slug"),
        db.Index("ix_categories_slug", "slug"),
    )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), nullable=False)

    articles = db.relationship(
        "Article", back_populates="category", passive_deletes=True
    )
