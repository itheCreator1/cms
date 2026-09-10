"""add announcement review status

Revision ID: 5e2d9a6b1c44
Revises: 739941d28772
Create Date: 2026-09-10

"""
from alembic import op


revision = "5e2d9a6b1c44"
down_revision = "739941d28772"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        "ALTER TYPE announcement_status "
        "ADD VALUE IF NOT EXISTS 'pending_review' BEFORE 'published'"
    )


def downgrade():
    op.execute(
        "UPDATE announcements SET status = 'draft' "
        "WHERE status = 'pending_review'"
    )
    op.execute("ALTER TABLE announcements ALTER COLUMN status DROP DEFAULT")
    op.execute("ALTER TYPE announcement_status RENAME TO announcement_status_old")
    op.execute("CREATE TYPE announcement_status AS ENUM ('draft', 'published')")
    op.execute(
        "ALTER TABLE announcements ALTER COLUMN status TYPE announcement_status "
        "USING status::text::announcement_status"
    )
    op.execute(
        "ALTER TABLE announcements ALTER COLUMN status SET DEFAULT 'draft'"
    )
    op.execute("DROP TYPE announcement_status_old")
