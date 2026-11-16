"""Settings for each environment: development, testing and production."""

import os

from dotenv import load_dotenv

# Read the local .env file (if there is one) into environment variables.
# On Render there is no .env file; the variables are set in the dashboard.
load_dotenv()


class BaseConfig:
    """Settings shared by every environment."""

    # The session cookie cannot be read by JavaScript, and is not sent when
    # another website makes a request to ours.
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    # Used only when SECRET_KEY is missing from the environment.
    # None means "there is no fallback, refuse to start".
    FALLBACK_SECRET_KEY = None


class DevConfig(BaseConfig):
    DEBUG = True
    FALLBACK_SECRET_KEY = "dev-only-not-a-secret"


class TestConfig(BaseConfig):
    TESTING = True
    FALLBACK_SECRET_KEY = "test-only-not-a-secret"


class ProdConfig(BaseConfig):
    # Only send the session cookie over HTTPS.
    SESSION_COOKIE_SECURE = True


CONFIGS = {
    "development": DevConfig,
    "testing": TestConfig,
    "production": ProdConfig,
}


def load_secret_key(config_class):
    """Return the key Flask uses to sign session cookies.

    Development and testing fall back to a throwaway key so the app runs
    without any setup. Production has no fallback: a guessable key would let
    anyone forge a login session, so we stop instead of starting unsafely.
    """
    secret_key = os.environ.get("SECRET_KEY") or config_class.FALLBACK_SECRET_KEY
    if not secret_key:
        raise RuntimeError(
            "SECRET_KEY is not set. Set it as an environment variable "
            "before starting Huddle in production."
        )
    return secret_key
