import os

import click
from flask.cli import with_appcontext

from backend.extensions import db
from backend.models import Category, User, UserRole
from backend.utils.validation import normalize_email


INITIAL_CATEGORIES = (
    ("General", "general"),
    ("News", "news"),
    ("Announcements", "announcements"),
)


@click.command("seed")
@with_appcontext
def seed_command():
    email_value = os.getenv("SEED_SUPERADMIN_EMAIL")
    password = os.getenv("SEED_SUPERADMIN_PASSWORD")
    if not email_value or not password:
        raise click.ClickException(
            "SEED_SUPERADMIN_EMAIL and SEED_SUPERADMIN_PASSWORD are required"
        )

    email = normalize_email(email_value)
    if email is None or not 12 <= len(password) <= 128:
        raise click.ClickException("Seed credentials are invalid")

    user = db.session.execute(
        db.select(User).where(User.email == email)
    ).scalar_one_or_none()
    if user is None:
        user = User(email=email)
        db.session.add(user)
    user.role = UserRole.SUPERADMIN
    user.set_password(password)

    for name, slug in INITIAL_CATEGORIES:
        name_match = db.session.execute(
            db.select(Category).where(Category.name == name)
        ).scalar_one_or_none()
        slug_match = db.session.execute(
            db.select(Category).where(Category.slug == slug)
        ).scalar_one_or_none()
        # Either unique identifier being occupied makes insertion destructive or
        # invalid. Preserve existing taxonomy and skip that seed category.
        if name_match is None and slug_match is None:
            db.session.add(Category(name=name, slug=slug))

    db.session.commit()
    click.echo("Seed data is ready.")
