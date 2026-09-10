from backend.extensions import db


class Media(db.Model):
    __tablename__ = "media"
    __table_args__ = (db.UniqueConstraint("url", name="uq_media_url"),)

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

    uploader = db.relationship("User", back_populates="media")
    featured_articles = db.relationship(
        "Article", back_populates="featured_image", passive_deletes=True
    )
