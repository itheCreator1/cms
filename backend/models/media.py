from backend.extensions import db


class Media(db.Model):
    __tablename__ = "media"
    __table_args__ = (
        db.UniqueConstraint("url", name="uq_media_url"),
        db.UniqueConstraint("storage_key", name="uq_media_storage_key"),
    )

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(2048), nullable=False)
    uploaded_by = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    uploaded_at = db.Column(
        db.DateTime(timezone=True), nullable=False, server_default=db.func.now()
    )
    file_type = db.Column(db.String(255), nullable=False)
    source_type = db.Column(
        db.String(32), nullable=False, default="upload", server_default="upload"
    )
    media_type = db.Column(
        db.String(32), nullable=False, default="image", server_default="image"
    )
    provider = db.Column(db.String(64), nullable=True)
    storage_key = db.Column(db.String(255), nullable=True)
    alt_text = db.Column(db.String(500), nullable=True)

    uploader = db.relationship("User", back_populates="media")
    featured_articles = db.relationship(
        "Article", back_populates="featured_image", passive_deletes=True
    )
