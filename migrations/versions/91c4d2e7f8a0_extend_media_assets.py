"""extend media assets

Revision ID: 91c4d2e7f8a0
Revises: 5e2d9a6b1c44
Create Date: 2026-09-10

"""
from alembic import op
import sqlalchemy as sa


revision = "91c4d2e7f8a0"
down_revision = "5e2d9a6b1c44"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "media",
        sa.Column(
            "source_type",
            sa.String(length=32),
            server_default="upload",
            nullable=False,
        ),
    )
    op.add_column(
        "media",
        sa.Column(
            "media_type",
            sa.String(length=32),
            server_default="image",
            nullable=False,
        ),
    )
    op.add_column("media", sa.Column("provider", sa.String(length=64)))
    op.add_column("media", sa.Column("storage_key", sa.String(length=255)))
    op.add_column("media", sa.Column("alt_text", sa.String(length=500)))
    op.create_unique_constraint("uq_media_storage_key", "media", ["storage_key"])


def downgrade():
    op.drop_constraint("uq_media_storage_key", "media", type_="unique")
    op.drop_column("media", "alt_text")
    op.drop_column("media", "storage_key")
    op.drop_column("media", "provider")
    op.drop_column("media", "media_type")
    op.drop_column("media", "source_type")
