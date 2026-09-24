"""Create disposable accounts and taxonomy for browser acceptance tests."""

from backend.app import create_app
from backend.extensions import db
from backend.models import Category, User, UserRole


USERS = (
    ("publisher.e2e@example.test", "publisher e2e test password", UserRole.PUBLISHER),
    ("admin.e2e@example.test", "admin e2e test password", UserRole.ADMIN),
)


def main():
    app = create_app()
    with app.app_context():
        for email, password, role in USERS:
            user = db.session.scalar(db.select(User).where(User.email == email))
            if user is None:
                user = User(email=email)
                db.session.add(user)
            user.role = role
            user.set_password(password)

        category = db.session.scalar(
            db.select(Category).where(Category.slug == "e2e-news")
        )
        if category is None:
            db.session.add(Category(name="E2E News", slug="e2e-news"))
        db.session.commit()


if __name__ == "__main__":
    main()
