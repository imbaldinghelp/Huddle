from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, Length, ValidationError

from app.auth.service import normalise_username, username_error


def strip_text(value):
    return (value or "").strip()


class CreatePlayerForm(FlaskForm):
    display_name = StringField(
        "Name",
        validators=[DataRequired(message="Enter the player's name."), Length(max=60)],
        filters=[strip_text],
    )
    username = StringField(
        "Username",
        validators=[DataRequired(message="Enter a username.")],
        filters=[normalise_username],
    )

    def validate_username(self, field):
        error = username_error(field.data)
        if error:
            raise ValidationError(error)


class ConfirmActionForm(FlaskForm):
    """A form with no fields. It exists to carry the CSRF token on action buttons."""
