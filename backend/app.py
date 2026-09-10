from flask import Flask, jsonify, request
from flask_cors import CORS

from backend import models  # noqa: F401 -- import models for migration discovery
from backend.config import Config
from backend.extensions import db, migrate
from backend.routes import blueprints


def create_app(config_object=Config):
    app = Flask(__name__)
    app.json.compact = True
    app.config.from_object(config_object)

    db.init_app(app)
    migrate.init_app(app, db)
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

    return app
