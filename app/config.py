"""Settings for the two environments: development (also used by tests) and production."""

import os
from datetime import timedelta

from dotenv import load_dotenv

# Read the local .env file (if there is one) into environment variables.
# On Render there is no .env file; the variables are set in the dashboard.
load_dotenv()


def database_url():
    """Return where the database lives.

    DATABASE_URL (for example Neon PostgreSQL) wins when it is set. Otherwise
    we use a SQLite file inside the instance/ folder, which needs no setup.
    """
    url = os.environ.get("DATABASE_URL")
    if not url:
        return "sqlite:///huddle.db"
    # Some hosts still hand out the old "postgres://" prefix, which SQLAlchemy rejects.
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return url


def model_list(text):
    """Turn "model-a, model-b" from the environment into ["model-a", "model-b"]."""
    return [name.strip() for name in text.split(",") if name.strip()]


class BaseConfig:
    """Settings shared by every environment."""

    SQLALCHEMY_DATABASE_URI = database_url()

    # ---------- AI assistant ----------
    # Model names are written the LiteLLM way: "<provider>/<model>". Each
    # provider's API key is read from its own environment variable
    # (GROQ_API_KEY, GEMINI_API_KEY, ...); see .env.example.
    LLM_MODEL = os.environ.get("LLM_MODEL") or "groq/llama-3.3-70b-versatile"
    # Tried in order when the main model fails or is over its free limit.
    LLM_FALLBACK_MODELS = model_list(
        os.environ.get("LLM_FALLBACK_MODELS") or "gemini/gemini-3.5-flash-lite"
    )
    # Give up on a model that has not answered after this many seconds.
    LLM_TIMEOUT_SECONDS = 20
    # How many questions one user may ask per day.
    ASSISTANT_DAILY_LIMIT = int(os.environ.get("ASSISTANT_DAILY_LIMIT") or 20)

    # The session cookie cannot be read by JavaScript, and is not sent when
    # another website makes a request to ours.
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    # How long someone stays logged in on the same device.
    PERMANENT_SESSION_LIFETIME = timedelta(days=14)

    # A form's security (CSRF) token stays valid for as long as the login
    # session, not just one hour. Building a play in the court editor can take
    # longer than that, and the save must still go through.
    WTF_CSRF_TIME_LIMIT = None

    # Refuse request bodies over 256 KB. A saved play is a few KB at most.
    MAX_CONTENT_LENGTH = 256 * 1024

    # Login attempt counts are kept in memory. Fine for one small server.
    RATELIMIT_STORAGE_URI = "memory://"
    LOGIN_RATE_LIMIT = "5 per minute"

    # Used only when SECRET_KEY is missing from the environment.
    # None means "there is no fallback, refuse to start".
    FALLBACK_SECRET_KEY = None


class DevConfig(BaseConfig):
    """Local development and automated tests."""

    DEBUG = True
    FALLBACK_SECRET_KEY = "dev-only-not-a-secret"


class ProdConfig(BaseConfig):
    # Only send the session cookie over HTTPS.
    SESSION_COOKIE_SECURE = True


CONFIGS = {
    "development": DevConfig,
    "production": ProdConfig,
}


def load_secret_key(config_class):
    """Return the key Flask uses to sign session cookies.

    Development (and tests) fall back to a throwaway key so the app runs
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
