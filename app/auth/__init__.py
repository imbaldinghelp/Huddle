"""Auth blueprint: the login page (and, from Phase 1, logging in and out)."""

from flask import Blueprint

auth_bp = Blueprint("auth", __name__)

# Imported at the bottom on purpose: routes.py needs auth_bp to exist first.
from app.auth import routes  # noqa: E402, F401
