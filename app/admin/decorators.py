from functools import wraps

from flask import abort
from flask_login import current_user, login_required


def admin_required(view):
    """Allow only logged-in admins to open a route.

    Visitors who are not logged in are sent to the login page.
    Logged-in players get a 403 "not allowed" page.
    """

    @wraps(view)
    @login_required
    def wrapped(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)
        return view(*args, **kwargs)

    return wrapped
