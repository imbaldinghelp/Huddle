"""Huddle application package.

create_app() is an "application factory": instead of one global Flask app,
we build a fresh app on demand. Tests use this to get a clean app with test
settings, and run.py uses it to get the real one.
"""

import os

from flask import Flask

from app.config import CONFIGS, load_secret_key
from app.extensions import csrf, db, limiter, login_manager, migrate


def create_app(config_name=None, overrides=None):
    """Build and return a configured Flask app.

    config_name is "development" or "production". When it is not given, the
    FLASK_CONFIG environment variable decides (default: development).
    overrides is a dict of settings that replace the config's values; the
    tests use it to point the app at a throwaway database.
    """
    config_name = config_name or os.environ.get("FLASK_CONFIG", "development")
    config_class = CONFIGS[config_name]

    app = Flask(__name__)
    app.config.from_object(config_class)
    app.config["SECRET_KEY"] = load_secret_key(config_class)
    app.config.update(overrides or {})

    register_extensions(app)
    register_blueprints(app)
    register_extras(app)
    return app


def register_extensions(app):
    """Attach the database, login sessions, CSRF protection and rate limiting."""
    # Importing the models here makes sure the database layer knows every table.
    from app import models  # noqa: F401

    db.init_app(app)
    # render_as_batch lets migrations change existing tables on SQLite.
    migrate.init_app(app, db, render_as_batch=True)
    login_manager.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)


def register_blueprints(app):
    """Attach each feature's routes to the app. New feature = new blueprint."""
    # Imported here, not at the top, so blueprints can import from `app`
    # (for example the database) without a circular import.
    from app.admin import admin_bp
    from app.auth import auth_bp
    from app.playbook import playbook_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(playbook_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")


def register_extras(app):
    """Attach error pages and command-line commands."""
    from app.cli import register_cli
    from app.errors import register_error_handlers

    register_error_handlers(app)
    register_cli(app)
