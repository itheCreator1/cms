from backend.extensions import db


class ArticleBodyBlock(db.Model):
    __tablename__ = "article_body_blocks"
    __table_args__ = (db.UniqueConstraint("article_id", "position", name="uq_article_block_position"),)

    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey("articles.id", ondelete="CASCADE"), nullable=False)
    position = db.Column(db.Integer, nullable=False)
    text = db.Column(db.Text, nullable=True)
    media_id = db.Column(db.Integer, db.ForeignKey("media.id", ondelete="RESTRICT"), nullable=True)
    media = db.relationship("Media")


class AnnouncementBodyBlock(db.Model):
    __tablename__ = "announcement_body_blocks"
    __table_args__ = (db.UniqueConstraint("announcement_id", "position", name="uq_announcement_block_position"),)

    id = db.Column(db.Integer, primary_key=True)
    announcement_id = db.Column(db.Integer, db.ForeignKey("announcements.id", ondelete="CASCADE"), nullable=False)
    position = db.Column(db.Integer, nullable=False)
    text = db.Column(db.Text, nullable=True)
    media_id = db.Column(db.Integer, db.ForeignKey("media.id", ondelete="RESTRICT"), nullable=True)
    media = db.relationship("Media")


class PageBodyBlock(db.Model):
    __tablename__ = "page_body_blocks"
    __table_args__ = (db.UniqueConstraint("page_id", "position", name="uq_page_block_position"),)

    id = db.Column(db.Integer, primary_key=True)
    page_id = db.Column(db.Integer, db.ForeignKey("pages.id", ondelete="CASCADE"), nullable=False)
    position = db.Column(db.Integer, nullable=False)
    text = db.Column(db.Text, nullable=True)
    media_id = db.Column(db.Integer, db.ForeignKey("media.id", ondelete="RESTRICT"), nullable=True)
    media = db.relationship("Media")
