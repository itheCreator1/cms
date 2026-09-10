from flask import Flask, jsonify, request
from flask_cors import CORS

from backend import models  # noqa: F401 -- import models for migration discovery
from backend.config import Config
from backend.extensions import db, jwt, limiter, migrate
from backend.routes import blueprints
from backend.commands import seed_command
from backend.utils.security_logging import configure_security_logging


def create_app(config_object=Config):
    app = Flask(__name__)
    app.json.compact = True
    app.config.from_object(config_object)
    app.config.setdefault("RATELIMIT_STORAGE_URI", "memory://")

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    limiter.init_app(app)
    configure_security_logging()
    app.cli.add_command(seed_command)
    CORS(
        app,
        resources={r"/api/*": {"origins": [app.config["FRONTEND_ORIGIN"]]}},
    )

    for blueprint in blueprints:
        app.register_blueprint(blueprint)

    @app.get("/api/health")
    def health():
        return jsonify(status="ok")

    @app.errorhandler(404)
    def not_found(error):
        if request.path.startswith("/api/"):
            return jsonify(error="Not found"), 404
        return error

    @app.errorhandler(429)
    def rate_limit_exceeded(_error):
        return jsonify(error="Rate limit exceeded"), 429

    return app
