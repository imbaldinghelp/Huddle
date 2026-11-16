import pytest

from app import create_app


def test_app_uses_development_config(app):
    assert app.config["TESTING"] is True
    assert app.config["SESSION_COOKIE_SECURE"] is False


@pytest.mark.parametrize("path", ["/", "/login"])
def test_login_page_loads(client, path):
    response = client.get(path)

    assert response.status_code == 200
    assert b"Welcome back." in response.data


@pytest.mark.parametrize(
    "path",
    [
        "/static/css/tokens.css",
        "/static/css/base.css",
        "/static/css/components.css",
        "/static/css/pages/login.css",
        "/static/js/password-toggle.js",
        "/static/images/sutd_team.jpg",
    ],
)
def test_login_page_assets_exist(client, path):
    assert client.get(path).status_code == 200


def test_production_refuses_to_start_without_secret_key(monkeypatch):
    monkeypatch.delenv("SECRET_KEY", raising=False)

    with pytest.raises(RuntimeError, match="SECRET_KEY"):
        create_app("production")


def test_production_starts_with_secret_key(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "a-real-secret-for-this-test")

    app = create_app("production")

    assert app.config["SESSION_COOKIE_SECURE"] is True
