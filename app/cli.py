"""Extra `flask` commands, run from the terminal."""

import click

from app.auth.service import create_user, normalise_username, password_error, username_error
from app.constants import Role


def prompt_until_valid(label, find_error, clean=str.strip, **prompt_options):
    """Keep asking until the answer passes the check."""
    while True:
        value = clean(click.prompt(label, **prompt_options))
        error = find_error(value)
        if error is None:
            return value
        click.echo(f"  {error}")


def display_name_error(name):
    if not name or len(name) > 60:
        return "Enter a name of 1 to 60 characters."
    return None


def register_cli(app):
    @app.cli.command("create-admin")
    def create_admin():
        """Create an admin account (captain or coach)."""
        username = prompt_until_valid("Username", username_error, clean=normalise_username)
        display_name = prompt_until_valid("Display name", display_name_error)
        password = prompt_until_valid(
            "Password",
            password_error,
            clean=lambda value: value,
            hide_input=True,
            confirmation_prompt=True,
        )
        create_user(username, display_name, Role.ADMIN, password, must_change_password=False)
        click.echo(f"Admin '{username}' created. You can now log in.")
