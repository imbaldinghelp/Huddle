from flask import abort, flash, make_response, redirect, render_template, url_for
from flask_login import current_user

from app.admin import admin_bp, service
from app.admin.decorators import admin_required
from app.admin.forms import ConfirmActionForm, CreatePlayerForm
from app.extensions import db
from app.models.user import User


def get_user_or_404(user_id):
    user = db.session.get(User, user_id)
    if user is None:
        abort(404)
    return user


def require_valid_action_form():
    """Action buttons post an empty form; reject it if the CSRF token is missing."""
    if not ConfirmActionForm().validate_on_submit():
        abort(400)


def show_credentials_once(user, temp_password, heading):
    """Render the temporary password straight into the page.

    It is never saved or put in the session, and the browser is told not to
    cache the page, so it cannot be seen again after the admin leaves.
    """
    page = render_template(
        "admin/player_credentials.html", user=user, temp_password=temp_password, heading=heading
    )
    response = make_response(page)
    response.headers["Cache-Control"] = "no-store"
    return response


@admin_bp.route("/")
@admin_required
def index():
    return redirect(url_for("admin.players"))


@admin_bp.route("/players")
@admin_required
def players():
    return render_template(
        "admin/players.html", users=service.list_users(), action_form=ConfirmActionForm()
    )


@admin_bp.route("/players/new", methods=["GET", "POST"])
@admin_required
def new_player():
    form = CreatePlayerForm()
    if form.validate_on_submit():
        user, temp_password = service.create_player(form.username.data, form.display_name.data)
        return show_credentials_once(user, temp_password, heading="Player created.")
    return render_template("admin/new_player.html", form=form)


@admin_bp.route("/players/<int:user_id>/reset-password", methods=["POST"])
@admin_required
def reset_player_password(user_id):
    require_valid_action_form()
    user = get_user_or_404(user_id)
    try:
        temp_password = service.reset_password(user, acting_admin=current_user)
    except service.AccountActionError as error:
        flash(str(error), "error")
        return redirect(url_for("admin.players"))
    return show_credentials_once(user, temp_password, heading="Password reset.")


@admin_bp.route("/players/<int:user_id>/deactivate", methods=["POST"])
@admin_required
def deactivate_player(user_id):
    return change_active_state(user_id, active=False)


@admin_bp.route("/players/<int:user_id>/reactivate", methods=["POST"])
@admin_required
def reactivate_player(user_id):
    return change_active_state(user_id, active=True)


def change_active_state(user_id, active):
    require_valid_action_form()
    user = get_user_or_404(user_id)
    try:
        service.set_active(user, active, acting_admin=current_user)
    except service.AccountActionError as error:
        flash(str(error), "error")
    else:
        state = "reactivated" if active else "deactivated"
        flash(f"{user.display_name} has been {state}.", "success")
    return redirect(url_for("admin.players"))
