"""Shared pytest fixtures. pytest passes these to any test that names them."""

import pytest

from app import create_app


@pytest.fixture
def app():
    """A fresh Huddle app using the testing settings."""
    return create_app("testing")


@pytest.fixture
def client(app):
    """A fake browser that makes requests to the app without a real server."""
    return app.test_client()
