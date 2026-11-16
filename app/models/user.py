from datetime import datetime, timezone

from flask_login import UserMixin
from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column
from werkzeug.security import check_password_hash, generate_password_hash

from app.constants import Role
from app.extensions import db


def utc_now():
    return datetime.now(timezone.utc)


class User(UserMixin, db.Model):
    """Someone who can log in: an admin (captain/coach) or a player."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    # Always stored in lowercase so "Brian" and "brian" are the same account.
    username: Mapped[str] = mapped_column(String(30), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    display_name: Mapped[str] = mapped_column(String(60))
    role: Mapped[str] = mapped_column(String(20), default=Role.PLAYER)
    # Deactivated users keep their row (we never delete users) but cannot log in.
    is_active: Mapped[bool] = mapped_column(default=True)
    # True while the user still has the temporary password an admin gave them.
    must_change_password: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    @property
    def is_admin(self):
        return self.role == Role.ADMIN

    def set_password(self, password):
        """Store a one-way hash of the password, never the password itself."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"
