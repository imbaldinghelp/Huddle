"""Entry point: `flask run` (and gunicorn in production) load `app` from here."""

from app import create_app

app = create_app()
