"""Account logic: checking logins, creating users and changing passwords.

Routes and the command line both call these functions, so the rules live in
one place.
"""

import re
import secrets

from sqlalchemy import select
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db
from app.models.user import User, utc_now

MIN_PASSWORD_LENGTH = 8
USERNAME_PATTERN = re.compile(r"^[a-z0-9._-]{3,30}$")
USERNAME_RULE = "Use 3 to 30 characters: lowercase letters, numbers, dots, dashes or underscores."

WRONG_LOGIN_MESSAGE = "Wrong username or password."
DEACTIVATED_MESSAGE = "This account is deactivated. Ask your captain or coach to reactivate it."

# Letters and digits that are hard to mix up when read off a screen (no 0/O, 1/l/I).
TEMP_PASSWORD_ALPHABET = "abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789"
TEMP_PASSWORD_LENGTH = 12

# Checked when the username does not exist, so a wrong username takes as long
# to reject as a wrong password and cannot be told apart by timing.
_DUMMY_HASH = generate_password_hash("not-a-real-password")


def normalise_username(raw):
    return (raw or "").strip().lower()


def username_error(username):
    """Return a message when the username is not allowed, otherwise None."""
    if not USERNAME_PATTERN.match(username):
        return USERNAME_RULE
    if find_user(username) is not None:
        return "That username is already taken."
    return None


def password_error(password):
    """Return a message when the password is too weak, otherwise None."""
    if len(password) < MIN_PASSWORD_LENGTH:
        return f"Use at least {MIN_PASSWORD_LENGTH} characters."
    return None


def find_user(username):
    return db.session.scalar(select(User).where(User.username == normalise_username(username)))


def authenticate(username, password):
    """Check a login attempt. Returns (user, None) or (None, error message)."""
    user = find_user(username)
    if user is None:
        check_password_hash(_DUMMY_HASH, password)
        return None, WRONG_LOGIN_MESSAGE
    if not user.check_password(password):
        return None, WRONG_LOGIN_MESSAGE
    # Only said after a correct password, so it gives nothing away to a guesser.
    if not user.is_active:
        return None, DEACTIVATED_MESSAGE
    return user, None


def record_login(user):
    user.last_login_at = utc_now()
    db.session.commit()


def create_user(username, display_name, role, password, must_change_password):
    user = User(
        username=normalise_username(username),
        display_name=display_name.strip(),
        role=role,
        must_change_password=must_change_password,
    )
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user


def change_password(user, new_password):
    """Set the user's own chosen password and lift the forced-change flag."""
    user.set_password(new_password)
    user.must_change_password = False
    db.session.commit()


def generate_temp_password():
    return "".join(secrets.choice(TEMP_PASSWORD_ALPHABET) for _ in range(TEMP_PASSWORD_LENGTH))
