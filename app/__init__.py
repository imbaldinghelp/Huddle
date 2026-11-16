"""Huddle application package.

create_app() is an "application factory": instead of one global Flask app,
we build a fresh app on demand. Tests use this to get a clean app with test
settings, and run.py uses it to get the real one.
"""

import os

from flask import Flask

from app.config import CONFIGS, load_secret_key


def create_app(config_name=None):
    """Build and return a configured Flask app.

    config_name is "development", "testing" or "production". When it is not
    given, the FLASK_CONFIG environment variable decides (default: development).
    """
    config_name = config_name or os.environ.get("FLASK_CONFIG", "development")
    config_class = CONFIGS[config_name]

    app = Flask(__name__)
    app.config.from_object(config_class)
    app.config["SECRET_KEY"] = load_secret_key(config_class)

    register_blueprints(app)
    return app


def register_blueprints(app):
    """Attach each feature's routes to the app. New feature = new blueprint."""
    # Imported here, not at the top, so blueprints can import from `app`
    # later (for example the database) without a circular import.
    from app.auth import auth_bp

    app.register_blueprint(auth_bp)
