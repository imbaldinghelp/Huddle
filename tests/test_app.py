import pytest

from app import create_app


def test_app_uses_development_config(app):
    assert app.config["TESTING"] is True
    assert app.config["SESSION_COOKIE_HTTPONLY"] is True
    assert app.config["SESSION_COOKIE_SAMESITE"] == "Lax"
    assert app.config["SESSION_COOKIE_SECURE"] is False


def test_login_page_loads(client):
    response = client.get("/login")

    assert response.status_code == 200
    assert b"Welcome back." in response.data


def test_home_sends_visitors_to_login(client):
    response = client.get("/")

    assert response.status_code == 302
    assert response.headers["Location"] == "/login"


@pytest.mark.parametrize(
    "path",
    [
        "/static/css/tokens.css",
        "/static/css/base.css",
        "/static/css/components.css",
        "/static/css/pages/login.css",
        "/static/css/pages/admin.css",
        "/static/css/pages/error.css",
        "/static/js/password-toggle.js",
        "/static/js/confirm-submit.js",
        "/static/css/pages/playbook.css",
        "/static/css/pages/play.css",
        "/static/css/pages/play-editor.css",
        "/static/js/play-viewer.js",
        "/static/js/play-editor.js",
        "/static/js/court/court.js",
        "/static/js/court/render.js",
        "/static/icons/category-offense.svg",
        "/static/icons/line-cut.svg",
        "/static/images/sutd_team.jpg",
    ],
)
def test_static_files_exist(client, path):
    assert client.get(path).status_code == 200


def test_javascript_is_served_with_a_type_browsers_accept(client):
    # Browsers refuse to run JavaScript modules that arrive labelled as plain text.
    assert client.get("/static/js/court/court.js").mimetype == "text/javascript"


def test_unknown_page_shows_404_page(client):
    response = client.get("/no-such-page")

    assert response.status_code == 404
    assert b"Page not found." in response.data


def test_production_refuses_to_start_without_secret_key(monkeypatch):
    monkeypatch.delenv("SECRET_KEY", raising=False)

    with pytest.raises(RuntimeError, match="SECRET_KEY"):
        create_app("production")


def test_production_starts_with_secret_key(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "a-real-secret-for-this-test")

    app = create_app("production", {"SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"})

    assert app.config["SESSION_COOKIE_SECURE"] is True
