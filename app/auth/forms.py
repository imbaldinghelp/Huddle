from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField
from wtforms.validators import DataRequired, EqualTo, ValidationError

from app.auth.service import normalise_username, password_error


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()], filters=[normalise_username])
    password = PasswordField("Password", validators=[DataRequired()])


class SetPasswordForm(FlaskForm):
    """Used on first login: the user has just typed their temporary password."""

    new_password = PasswordField("New password", validators=[DataRequired()])
    confirm_password = PasswordField(
        "Confirm new password",
        validators=[DataRequired(), EqualTo("new_password", message="The two passwords do not match.")],
    )

    def validate_new_password(self, field):
        error = password_error(field.data)
        if error:
            raise ValidationError(error)
        if current_user.check_password(field.data):
            raise ValidationError("Choose a password that is different from your current one.")


class ChangePasswordForm(SetPasswordForm):
    """Used when a user changes their password by choice: also asks for the current one."""

    current_password = PasswordField("Current password", validators=[DataRequired()])

    def validate_current_password(self, field):
        if not current_user.check_password(field.data):
            raise ValidationError("That is not your current password.")
