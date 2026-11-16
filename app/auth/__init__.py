"""Auth blueprint: logging in and out, and changing your password."""

from flask import Blueprint

auth_bp = Blueprint("auth", __name__)

# Imported at the bottom on purpose: these files need auth_bp to exist first.
from app.auth import hooks, routes  # noqa: E402, F401
