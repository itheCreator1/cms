from enum import Enum

from werkzeug.security import check_password_hash, generate_password_hash

from backend.extensions import db


class UserRole(str, Enum):
    VISITOR = "visitor"
    PUBLISHER = "publisher"
    ADMIN = "admin"
    SUPERADMIN = "superadmin"


class User(db.Model):
    __tablename__ = "users"
    __table_args__ = (db.UniqueConstraint("email", name="uq_users_email"),)

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(
        db.Enum(
            UserRole,
            name="user_role",
            values_callable=lambda enum: [member.value for member in enum],
            validate_strings=True,
        ),
        nullable=False,
        default=UserRole.VISITOR,
        server_default=UserRole.VISITOR.value,
    )
    created_at = db.Column(
        db.DateTime(timezone=True), nullable=False, server_default=db.func.now()
    )

    articles = db.relationship("Article", back_populates="author", passive_deletes=True)
    announcements = db.relationship(
        "Announcement", back_populates="author", passive_deletes=True
    )
    pages = db.relationship("Page", back_populates="author", passive_deletes=True)
    media = db.relationship("Media", back_populates="uploader", passive_deletes=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
