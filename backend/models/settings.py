from backend.extensions import db


class SiteSettings(db.Model):
    __tablename__ = "site_settings"
    __table_args__ = (db.CheckConstraint("id = 1", name="ck_site_settings_singleton"),)

    id = db.Column(db.Integer, primary_key=True)
    site_name = db.Column(db.String(120), nullable=False)
    tagline = db.Column(db.String(160), nullable=False)
    homepage_headline = db.Column(db.String(180), nullable=False)
    homepage_intro = db.Column(db.Text, nullable=False)


class SiteSettingsChange(db.Model):
    __tablename__ = "site_settings_changes"

    id = db.Column(db.Integer, primary_key=True)
    actor_id = db.Column(db.Integer, nullable=False)
    changed_at = db.Column(db.DateTime(timezone=True), nullable=False, server_default=db.func.now())
    before_values = db.Column(db.JSON, nullable=False)
    after_values = db.Column(db.JSON, nullable=False)
