"""add persistent site settings and change log

Revision ID: b7d9e0f2a4c6
Revises: a6c8d9e1f2b3
"""

from alembic import op
import sqlalchemy as sa


revision = "b7d9e0f2a4c6"
down_revision = "a6c8d9e1f2b3"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "site_settings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("site_name", sa.String(120), nullable=False),
        sa.Column("tagline", sa.String(160), nullable=False),
        sa.Column("homepage_headline", sa.String(180), nullable=False),
        sa.Column("homepage_intro", sa.Text(), nullable=False),
        sa.CheckConstraint("id = 1", name="ck_site_settings_singleton"),
    )
    op.create_table(
        "site_settings_changes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("actor_id", sa.Integer(), nullable=False),
        sa.Column("changed_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("before_values", sa.JSON(), nullable=False),
        sa.Column("after_values", sa.JSON(), nullable=False),
    )
    op.execute(
        sa.text("INSERT INTO site_settings (id, site_name, tagline, homepage_headline, homepage_intro) VALUES (1, :site_name, :tagline, :headline, :intro)").bindparams(
            site_name="CMS", tagline="The daily edition",
            headline="Stories that keep us connected.",
            intro="News, notices, and voices from across the community.",
        )
    )


def downgrade():
    op.drop_table("site_settings_changes")
    op.drop_table("site_settings")
