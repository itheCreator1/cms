"""add cms domain models

Revision ID: 739941d28772
Revises:
Create Date: 2026-09-10 07:03:48.179575

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '739941d28772'
down_revision = None
branch_labels = None
depends_on = None

user_role = postgresql.ENUM(
    'visitor', 'publisher', 'admin', 'superadmin',
    name='user_role',
    create_type=False,
)
article_status = postgresql.ENUM(
    'draft', 'pending_review', 'published',
    name='article_status',
    create_type=False,
)
announcement_status = postgresql.ENUM(
    'draft', 'published',
    name='announcement_status',
    create_type=False,
)
page_status = postgresql.ENUM(
    'draft', 'published',
    name='page_status',
    create_type=False,
)


def upgrade():
    bind = op.get_bind()
    user_role.create(bind, checkfirst=True)
    article_status.create(bind, checkfirst=True)
    announcement_status.create(bind, checkfirst=True)
    page_status.create(bind, checkfirst=True)

    op.create_table('categories',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('slug', sa.String(length=100), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_categories')),
    sa.UniqueConstraint('name', name='uq_categories_name'),
    sa.UniqueConstraint('slug', name='uq_categories_slug')
    )
    op.create_index('ix_categories_slug', 'categories', ['slug'], unique=False)

    op.create_table('tags',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('slug', sa.String(length=100), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_tags')),
    sa.UniqueConstraint('name', name='uq_tags_name'),
    sa.UniqueConstraint('slug', name='uq_tags_slug')
    )
    op.create_index('ix_tags_slug', 'tags', ['slug'], unique=False)

    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('password_hash', sa.String(length=255), nullable=False),
    sa.Column('role', user_role, server_default='visitor', nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_users')),
    sa.UniqueConstraint('email', name='uq_users_email')
    )
    op.create_table('announcements',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('body', sa.Text(), nullable=False),
    sa.Column('status', announcement_status, server_default='draft', nullable=False),
    sa.Column('author_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('published_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['author_id'], ['users.id'], name=op.f('fk_announcements_author_id_users'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_announcements'))
    )
    op.create_table('media',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('filename', sa.String(length=255), nullable=False),
    sa.Column('url', sa.String(length=2048), nullable=False),
    sa.Column('uploaded_by', sa.Integer(), nullable=False),
    sa.Column('uploaded_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('file_type', sa.String(length=255), nullable=False),
    sa.ForeignKeyConstraint(['uploaded_by'], ['users.id'], name=op.f('fk_media_uploaded_by_users'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_media')),
    sa.UniqueConstraint('url', name='uq_media_url')
    )
    op.create_table('pages',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('slug', sa.String(length=255), nullable=False),
    sa.Column('body', sa.Text(), nullable=False),
    sa.Column('status', page_status, server_default='draft', nullable=False),
    sa.Column('author_id', sa.Integer(), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['author_id'], ['users.id'], name=op.f('fk_pages_author_id_users'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_pages')),
    sa.UniqueConstraint('slug', name='uq_pages_slug')
    )
    op.create_index('ix_pages_slug', 'pages', ['slug'], unique=False)

    op.create_table('articles',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('slug', sa.String(length=255), nullable=False),
    sa.Column('body', sa.Text(), nullable=False),
    sa.Column('status', article_status, server_default='draft', nullable=False),
    sa.Column('author_id', sa.Integer(), nullable=False),
    sa.Column('category_id', sa.Integer(), nullable=False),
    sa.Column('featured_image_id', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('published_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['author_id'], ['users.id'], name=op.f('fk_articles_author_id_users'), ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['category_id'], ['categories.id'], name=op.f('fk_articles_category_id_categories'), ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['featured_image_id'], ['media.id'], name=op.f('fk_articles_featured_image_id_media'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_articles')),
    sa.UniqueConstraint('slug', name='uq_articles_slug')
    )
    op.create_index('ix_articles_slug', 'articles', ['slug'], unique=False)

    op.create_table('article_tags',
    sa.Column('article_id', sa.Integer(), nullable=False),
    sa.Column('tag_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['article_id'], ['articles.id'], name=op.f('fk_article_tags_article_id_articles'), ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], name=op.f('fk_article_tags_tag_id_tags'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('article_id', 'tag_id', name=op.f('pk_article_tags'))
    )


def downgrade():
    op.drop_table('article_tags')
    op.drop_index('ix_articles_slug', table_name='articles')
    op.drop_table('articles')
    op.drop_index('ix_pages_slug', table_name='pages')
    op.drop_table('pages')
    op.drop_table('media')
    op.drop_table('announcements')
    op.drop_table('users')
    op.drop_index('ix_tags_slug', table_name='tags')
    op.drop_table('tags')
    op.drop_index('ix_categories_slug', table_name='categories')
    op.drop_table('categories')

    bind = op.get_bind()
    page_status.drop(bind, checkfirst=True)
    announcement_status.drop(bind, checkfirst=True)
    article_status.drop(bind, checkfirst=True)
    user_role.drop(bind, checkfirst=True)
