"""Shared pytest fixtures. pytest passes these to any test that names them."""

import pytest

from app import create_app
from app.auth.service import create_user
from app.constants import Role
from app.extensions import db

PASSWORD = "correct-horse-battery"

# Settings that replace the development ones while tests run.
TEST_SETTINGS = {
    "TESTING": True,
    # A throwaway database that lives in memory and vanishes after each test.
    "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    # Off so tests can post forms without first fetching a token.
    # test_security.py turns both back on to check they work.
    "WTF_CSRF_ENABLED": False,
    "RATELIMIT_ENABLED": False,
}


def build_app(**extra_settings):
    """Create an app with an empty database. The app context stays open for the test."""
    app = create_app("development", {**TEST_SETTINGS, **extra_settings})
    context = app.app_context()
    context.push()
    db.create_all()
    return app, context


@pytest.fixture
def app():
    """A fresh Huddle app with an empty database."""
    app, context = build_app()
    yield app
    db.session.remove()
    context.pop()


@pytest.fixture
def client(app):
    """A fake browser that makes requests to the app without a real server."""
    return app.test_client()


@pytest.fixture
def admin(app):
    return create_user("coach", "Coach Tan", Role.ADMIN, PASSWORD, must_change_password=False)


@pytest.fixture
def player(app):
    return create_user("wei", "Wei Jie", Role.PLAYER, PASSWORD, must_change_password=False)


def login(client, username, password=PASSWORD):
    """Log in through the real login form."""
    return client.post("/login", data={"username": username, "password": password})
