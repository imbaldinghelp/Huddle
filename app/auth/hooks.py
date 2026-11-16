"""Code that runs around every request to keep login state correct."""

from flask import redirect, request, url_for
from flask_login import current_user

from app.auth import auth_bp
from app.extensions import db, login_manager
from app.models.user import User

login_manager.login_view = "auth.login"
# The login page explains itself, so no extra "please log in" message is needed.
login_manager.login_message = None

# Pages a user may still open before they have replaced a temporary password.
ALLOWED_BEFORE_PASSWORD_CHANGE = {"auth.change_password", "auth.logout", "static"}


@login_manager.user_loader
def load_user(user_id):
    """Turn the id stored in the session cookie back into a User.

    Returning None for a deactivated user logs them out on their next click,
    even if they were already logged in.
    """
    user = db.session.get(User, int(user_id))
    if user is None or not user.is_active:
        return None
    return user


@auth_bp.before_app_request
def require_password_change():
    """Send users with a temporary password to the change-password page first."""
    if not current_user.is_authenticated or not current_user.must_change_password:
        return None
    if request.endpoint in ALLOWED_BEFORE_PASSWORD_CHANGE:
        return None
    return redirect(url_for("auth.change_password"))
