"""Admin blueprint: pages only admins (captain/coach) may open."""

from flask import Blueprint

admin_bp = Blueprint("admin", __name__)

# Imported at the bottom on purpose: routes.py needs admin_bp to exist first.
from app.admin import routes  # noqa: E402, F401
