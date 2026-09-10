from enum import Enum

from backend.extensions import db


class AnnouncementStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"


class Announcement(db.Model):
    __tablename__ = "announcements"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    body = db.Column(db.Text, nullable=False)
    status = db.Column(
        db.Enum(
            AnnouncementStatus,
            name="announcement_status",
            values_callable=lambda enum: [member.value for member in enum],
            validate_strings=True,
        ),
        nullable=False,
        default=AnnouncementStatus.DRAFT,
        server_default=AnnouncementStatus.DRAFT.value,
    )
    author_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    created_at = db.Column(
        db.DateTime(timezone=True), nullable=False, server_default=db.func.now()
    )
    published_at = db.Column(db.DateTime(timezone=True), nullable=True)
    expires_at = db.Column(db.DateTime(timezone=True), nullable=True)

    author = db.relationship("User", back_populates="announcements")
