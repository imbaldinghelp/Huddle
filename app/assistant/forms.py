from flask_wtf import FlaskForm
from wtforms import TextAreaField
from wtforms.validators import DataRequired, Length

MAX_QUESTION_LENGTH = 500


def strip_text(value):
    return (value or "").strip()


class AskForm(FlaskForm):
    question = TextAreaField(
        "Your question",
        validators=[
            DataRequired(message="Type a question first."),
            Length(max=MAX_QUESTION_LENGTH, message=f"Keep it under {MAX_QUESTION_LENGTH} characters."),
        ],
        filters=[strip_text],
    )
