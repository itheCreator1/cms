from backend.routes.announcements import blueprint as announcements_blueprint
from backend.routes.articles import blueprint as articles_blueprint
from backend.routes.auth import blueprint as auth_blueprint
from backend.routes.categories import blueprint as categories_blueprint
from backend.routes.media import blueprint as media_blueprint
from backend.routes.pages import blueprint as pages_blueprint
from backend.routes.tags import blueprint as tags_blueprint
from backend.routes.users import blueprint as users_blueprint


blueprints = (
    auth_blueprint,
    articles_blueprint,
    announcements_blueprint,
    pages_blueprint,
    media_blueprint,
    categories_blueprint,
    tags_blueprint,
    users_blueprint,
)
