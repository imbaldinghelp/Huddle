from flask import abort, flash, jsonify, make_response, redirect, render_template, request, url_for
from flask_login import current_user

from app.admin import admin_bp, service
from app.admin.decorators import admin_required
from app.admin.forms import ConfirmActionForm, CreatePlayerForm
from app.constants import CATEGORY_LABELS, PlayStatus
from app.extensions import db
from app.models.user import User
from app.playbook import service as play_service
from app.playbook.validation import validate_play


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
    # The admin area is only for managing players; plays are managed from
    # the playbook itself (a category page, then Edit).
    return redirect(url_for("admin.players"))


# ---------- Players ----------


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


# ---------- Plays ----------
# There is no list of plays here: admins find them in the playbook. These
# routes are the court editor and the buttons on a category's Edit page.


def get_play_or_404(play_id):
    play = play_service.get_play(play_id)
    if play is None:
        abort(404)
    return play


def back_to_category(category):
    """Return to the Edit page of the category the play was in."""
    return redirect(url_for("playbook.edit_category", slug=category))


@admin_bp.route("/plays/new")
@admin_required
def new_play():
    # "New play" on a category page passes that category along (?category=offense).
    return render_template(
        "admin/play_editor.html",
        play=None,
        steps=[],
        categories=CATEGORY_LABELS,
        selected_category=play_service.find_category(request.args.get("category", "")),
        save_url=url_for("admin.create_play"),
    )


@admin_bp.route("/plays/<int:play_id>/edit")
@admin_required
def edit_play(play_id):
    play = get_play_or_404(play_id)
    return render_template(
        "admin/play_editor.html",
        play=play,
        steps=play_service.steps_data(play),
        categories=CATEGORY_LABELS,
        selected_category=play.category,
        save_url=url_for("admin.update_play", play_id=play.id),
    )


# The court editor saves with JavaScript: it posts the whole play as JSON
# (with the CSRF token in a header) and gets JSON back.
@admin_bp.route("/plays", methods=["POST"])
@admin_required
def create_play():
    return save_play_from_editor(play=None)


@admin_bp.route("/plays/<int:play_id>", methods=["POST"])
@admin_required
def update_play(play_id):
    return save_play_from_editor(get_play_or_404(play_id))


def save_play_from_editor(play):
    clean, errors = validate_play(request.get_json(silent=True))
    if errors:
        return jsonify(errors=errors), 400

    play = play_service.save_play(clean, author=current_user, play=play)
    # The editor opens the address we send back; the message shows on that page.
    # A published play goes to its category, where players will find it.
    if play.is_published:
        flash(f"{play.title} is published.", "success")
        return jsonify(redirect=url_for("playbook.category", slug=play.category))
    flash(f"{play.title} is saved as a draft.", "success")
    return jsonify(redirect=url_for("admin.edit_play", play_id=play.id))


@admin_bp.route("/plays/<int:play_id>/publish", methods=["POST"])
@admin_required
def publish_play(play_id):
    return change_play_status(play_id, PlayStatus.PUBLISHED, "is published.")


@admin_bp.route("/plays/<int:play_id>/unpublish", methods=["POST"])
@admin_required
def unpublish_play(play_id):
    return change_play_status(play_id, PlayStatus.DRAFT, "is back in drafts. Players can no longer see it.")


def change_play_status(play_id, status, outcome):
    require_valid_action_form()
    play = get_play_or_404(play_id)
    play_service.set_status(play, status)
    flash(f"{play.title} {outcome}", "success")
    return back_to_category(play.category)


@admin_bp.route("/plays/<int:play_id>/delete", methods=["POST"])
@admin_required
def delete_play(play_id):
    require_valid_action_form()
    play = get_play_or_404(play_id)
    title, category = play.title, play.category
    play_service.delete_play(play)
    flash(f"{title} has been deleted.", "success")
    return back_to_category(category)