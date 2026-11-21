from datetime import datetime, timedelta, timezone

from sqlalchemy import JSON, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.constants import CATEGORY_LABELS, PlayStatus
from app.extensions import db
from app.models.user import utc_now

# A play changed within this many days is marked "Updated" in the playbook.
RECENT_DAYS = 7


class Play(db.Model):
    """One play in the playbook, made of one or more steps."""

    __tablename__ = "plays"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(80))
    # One of the PlayCategory values, for example "offense".
    category: Mapped[str] = mapped_column(String(20), index=True)
    summary: Mapped[str] = mapped_column(String(200), default="")
    status: Mapped[str] = mapped_column(String(20), default=PlayStatus.DRAFT)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    # "delete-orphan" removes a play's steps from the database when the play
    # is deleted or when a step is taken out of this list.
    steps: Mapped[list["PlayStep"]] = relationship(
        back_populates="play",
        order_by="PlayStep.step_number",
        cascade="all, delete-orphan",
    )

    @property
    def is_published(self):
        return self.status == PlayStatus.PUBLISHED

    @property
    def category_label(self):
        return CATEGORY_LABELS[self.category]

    @property
    def is_recently_updated(self):
        updated_at = self.updated_at
        # SQLite hands dates back without a timezone; they were saved as UTC.
        if updated_at.tzinfo is None:
            updated_at = updated_at.replace(tzinfo=timezone.utc)
        return utc_now() - updated_at < timedelta(days=RECENT_DAYS)

    def __repr__(self):
        return f"<Play {self.title}>"


class PlayStep(db.Model):
    """One frame of a play: where everyone stands and what they do next."""

    __tablename__ = "play_steps"

    id: Mapped[int] = mapped_column(primary_key=True)
    play_id: Mapped[int] = mapped_column(ForeignKey("plays.id", ondelete="CASCADE"), index=True)
    # 1 for the first step, 2 for the second, and so on.
    step_number: Mapped[int]
    description: Mapped[str] = mapped_column(Text, default="")
    # Players, ball and arrows as JSON. The format is documented in
    # app/static/js/court/README.md and checked by app/playbook/validation.py.
    diagram: Mapped[dict] = mapped_column(JSON)

    play: Mapped[Play] = relationship(back_populates="steps")

    def __repr__(self):
        return f"<PlayStep {self.play_id}:{self.step_number}>"
