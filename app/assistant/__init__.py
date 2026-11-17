"""Assistant blueprint: the chat about a play.

The chat box is shown on the play page (app/templates/components/play_chat.html).
Its JavaScript sends each question to the one route in routes.py.
"""

from flask import Blueprint

assistant_bp = Blueprint("assistant", __name__)

# Imported at the bottom on purpose: routes.py needs assistant_bp to exist first.
from app.assistant import routes  # noqa: E402, F401
