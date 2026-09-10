import os

import click
from flask.cli import with_appcontext
from sqlalchemy import or_

from backend.extensions import db
from backend.models import Category, User, UserRole
from backend.routes.auth import EMAIL_PATTERN


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

    email = email_value.strip().casefold()
    if not EMAIL_PATTERN.fullmatch(email) or not 12 <= len(password) <= 128:
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
        category = db.session.execute(
            db.select(Category).where(or_(Category.name == name, Category.slug == slug))
        ).scalar_one_or_none()
        if category is None:
            db.session.add(Category(name=name, slug=slug))

    db.session.commit()
    click.echo("Seed data is ready.")
