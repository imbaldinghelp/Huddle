"""Player management done by admins: create, reset password, deactivate."""

from sqlalchemy import select

from app.auth.service import create_user, generate_temp_password
from app.constants import Role
from app.extensions import db
from app.models.user import User


class AccountActionError(Exception):
    """Raised when an admin tries something the account rules do not allow."""


def list_users():
    """Everyone with an account: active first, then by name."""
    query = select(User).order_by(User.is_active.desc(), User.display_name)
    return db.session.scalars(query).all()


def create_player(username, display_name):
    """Create a player with a temporary password. Returns (user, temp_password).

    The temporary password is returned so it can be shown to the admin once.
    Only its hash is saved.
    """
    temp_password = generate_temp_password()
    user = create_user(
        username=username,
        display_name=display_name,
        role=Role.PLAYER,
        password=temp_password,
        must_change_password=True,
    )
    return user, temp_password


def reset_password(user, acting_admin):
    """Give the user a new temporary password. Returns the temporary password."""
    if user.id == acting_admin.id:
        raise AccountActionError("Change your own password from your account page instead.")
    temp_password = generate_temp_password()
    user.set_password(temp_password)
    user.must_change_password = True
    db.session.commit()
    return temp_password


def set_active(user, active, acting_admin):
    """Deactivate or reactivate an account."""
    if user.id == acting_admin.id:
        raise AccountActionError("You cannot deactivate your own account.")
    user.is_active = active
    db.session.commit()
