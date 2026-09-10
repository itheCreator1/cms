import importlib

import pytest


@pytest.fixture()
def app(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite://")
    monkeypatch.setenv("FRONTEND_ORIGIN", "http://frontend.test")
    from backend.app import create_app

    application = create_app()
    application.config.update(TESTING=True)
    return application


@pytest.fixture()
def client(app):
    return app.test_client()


def test_factory_creates_application(app):
    assert app.name == "backend.app"


def test_health_returns_exact_contract(client):
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json == {"status": "ok"}
    assert response.get_data(as_text=True) == '{"status":"ok"}\n'


def test_health_contract_stays_compact_in_debug_mode(app):
    app.debug = True

    response = app.test_client().get("/api/health")

    assert response.get_data(as_text=True) == '{"status":"ok"}\n'


def test_api_allows_only_configured_frontend_origin(client):
    allowed = client.get("/api/health", headers={"Origin": "http://frontend.test"})
    denied = client.get("/api/health", headers={"Origin": "http://elsewhere.test"})

    assert allowed.headers["Access-Control-Allow-Origin"] == "http://frontend.test"
    assert "Access-Control-Allow-Origin" not in denied.headers


def test_unknown_api_route_returns_json_404(client):
    response = client.get("/api/does-not-exist")

    assert response.status_code == 404
    assert response.content_type == "application/json"
    assert response.json == {"error": "Not found"}


def test_unknown_non_api_route_keeps_normal_html_404(client):
    response = client.get("/does-not-exist")

    assert response.status_code == 404
    assert response.content_type.startswith("text/html")


@pytest.mark.parametrize(
    "module_name",
    [
        "auth",
        "articles",
        "announcements",
        "pages",
        "media",
        "categories",
        "tags",
        "users",
    ],
)
def test_placeholder_route_modules_import(module_name):
    importlib.import_module(f"backend.routes.{module_name}")


@pytest.mark.parametrize(
    "module_name",
    [
        "auth",
        "articles",
        "announcements",
        "pages",
        "media",
        "categories",
        "tags",
        "users",
    ],
)
def test_placeholder_model_modules_import(module_name):
    importlib.import_module(f"backend.models.{module_name}")
