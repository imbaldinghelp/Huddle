"""Shared pytest fixtures. pytest passes these to any test that names them."""

import pytest

from app import create_app
from app.auth.service import create_user
from app.constants import Role
from app.extensions import db
from app.playbook.service import save_play
from app.playbook.validation import validate_play

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
    # Fixed here so the assistant tests do not depend on what is in your .env.
    # No test ever calls a real model: test_assistant.py swaps in a fake.
    "LLM_MODEL": "groq/llama-3.3-70b-versatile",
    "LLM_FALLBACK_MODELS": ["gemini/gemini-3.5-flash-lite"],
    "ASSISTANT_DAILY_LIMIT": 20,
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


# ---------- Plays ----------

OFFENSE_SPOTS = {"O1": (0.5, 0.65), "O2": (0.81, 0.45), "O3": (0.19, 0.45), "O4": (0.32, 0.25), "O5": (0.68, 0.25)}


def diagram_data(**changes):
    """One valid step diagram: five attackers, the ball with player 1, a pass and a cut."""
    diagram = {
        "players": [
            {"id": player_id, "team": "offense", "x": x, "y": y} for player_id, (x, y) in OFFENSE_SPOTS.items()
        ],
        "ball": {"holder": "O1"},
        "actions": [
            {"type": "pass", "from": "O1", "to": "O2"},
            {"type": "cut", "player": "O3", "path": [[0.3, 0.4], [0.45, 0.2]]},
        ],
    }
    diagram.update(changes)
    return diagram


def play_data(**changes):
    """A whole valid play, in the form the court editor sends it."""
    play = {
        "title": "Horns Flare",
        "category": "offense",
        "summary": "Flare screen for the shooter.",
        "status": "published",
        "steps": [{"description": "1 passes to 2 on the wing.", "diagram": diagram_data()}],
    }
    play.update(changes)
    return play


def make_play(author, **changes):
    """Save a play straight to the database, skipping the browser."""
    clean, errors = validate_play(play_data(**changes))
    assert not errors, errors
    return save_play(clean, author=author)
