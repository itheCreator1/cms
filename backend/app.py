from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

from backend import models  # noqa: F401 -- import models for migration discovery
from backend.config import Config
from backend.extensions import create_limiter, db, jwt, migrate
from backend.routes import blueprints
from backend.routes.auth import configure_auth_rate_limits
from backend.commands import seed_command
from backend.utils.security_logging import configure_security_logging


def create_app(config_object=Config):
    app = Flask(__name__)
    app.json.compact = True
    app.config.from_object(config_object)
    app.config.setdefault("RATELIMIT_ENABLED", True)
    app.config.setdefault("RATELIMIT_STORAGE_URI", "memory://")

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    limiter = create_limiter(app)
    # Disabled limiter instances are not retained by Flask-Limiter itself, but
    # decorated views hold weak references and still need an app-lifetime owner.
    app.extensions["cms_limiter"] = limiter
    configure_security_logging()
    app.cli.add_command(seed_command)
    CORS(
        app,
        resources={r"/api/*": {"origins": [app.config["FRONTEND_ORIGIN"]]}},
    )

    for blueprint in blueprints:
        app.register_blueprint(blueprint)
    configure_auth_rate_limits(app, limiter)

    @app.get("/api/health")
    def health():
        return jsonify(status="ok")

    @app.errorhandler(HTTPException)
    def api_http_error(error):
        if request.path.startswith("/api/"):
            messages = {
                404: "Not found",
                405: "Method not allowed",
            }
            return jsonify(error=messages.get(error.code, error.name)), error.code
        return error

    @app.errorhandler(429)
    def rate_limit_exceeded(_error):
        return jsonify(error="Rate limit exceeded"), 429

    @app.errorhandler(500)
    def internal_server_error(error):
        if request.path.startswith("/api/"):
            return jsonify(error="Internal server error"), 500
        return error

    return app
