from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.extensions import db
from app.models.user import utc_now


class ChatLog(db.Model):
    """One question a user asked the assistant about a play, with the answer it gave.

    Only answered questions are saved. Counting a user's rows for today is how
    the daily question limit is enforced.
    """

    __tablename__ = "chat_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    # The play the user was looking at. Becomes empty if that play is deleted;
    # the question and answer stay.
    play_id: Mapped[int | None] = mapped_column(ForeignKey("plays.id", ondelete="SET NULL"), index=True)
    question: Mapped[str] = mapped_column(Text)
    answer: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    def __repr__(self):
        return f"<ChatLog {self.id} by user {self.user_id}>"
