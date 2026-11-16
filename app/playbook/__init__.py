"""Playbook blueprint: the pages players use to browse and view plays."""

from flask import Blueprint

playbook_bp = Blueprint("playbook", __name__)

# Imported at the bottom on purpose: routes.py needs playbook_bp to exist first.
from app.playbook import routes  # noqa: E402, F401
