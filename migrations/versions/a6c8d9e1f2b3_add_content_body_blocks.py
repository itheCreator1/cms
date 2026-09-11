"""add ordered content body blocks

Revision ID: a6c8d9e1f2b3
Revises: 91c4d2e7f8a0
Create Date: 2026-09-11
"""
from alembic import op
import sqlalchemy as sa


revision = "a6c8d9e1f2b3"
down_revision = "91c4d2e7f8a0"
branch_labels = None
depends_on = None


def _create_blocks_table(name, parent_table, parent_column, constraint_name):
    op.create_table(
        name,
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(parent_column, sa.Integer(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("text", sa.Text(), nullable=True),
        sa.Column("media_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint([parent_column], [f"{parent_table}.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["media_id"], ["media.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(parent_column, "position", name=constraint_name),
    )


def upgrade():
    _create_blocks_table("article_body_blocks", "articles", "article_id", "uq_article_block_position")
    _create_blocks_table("announcement_body_blocks", "announcements", "announcement_id", "uq_announcement_block_position")
    _create_blocks_table("page_body_blocks", "pages", "page_id", "uq_page_block_position")
    op.execute("INSERT INTO article_body_blocks (article_id, position, text) SELECT id, 0, body FROM articles")
    op.execute("INSERT INTO announcement_body_blocks (announcement_id, position, text) SELECT id, 0, body FROM announcements")
    op.execute("INSERT INTO page_body_blocks (page_id, position, text) SELECT id, 0, body FROM pages")


def downgrade():
    op.drop_table("page_body_blocks")
    op.drop_table("announcement_body_blocks")
    op.drop_table("article_body_blocks")
