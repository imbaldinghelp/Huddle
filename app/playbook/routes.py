from flask import abort, render_template
from flask_login import current_user, login_required

from app.admin.decorators import admin_required
from app.admin.forms import ConfirmActionForm
from app.assistant import service as assistant_service
from app.constants import CATEGORY_LABELS
from app.playbook import playbook_bp, service


@playbook_bp.route("/playbook")
@login_required
def index():
    return render_template("playbook/index.html", categories=service.list_categories())


@playbook_bp.route("/playbook/<slug>")
@login_required
def category(slug):
    return render_category(slug, editing=False)


# The same list with Edit, Publish/Unpublish and Delete on every play.
@playbook_bp.route("/playbook/<slug>/edit")
@admin_required
def edit_category(slug):
    return render_category(slug, editing=True)


def render_category(slug, editing):
    category = service.find_category(slug)
    if category is None:
        abort(404)
    return render_template(
        "playbook/category.html",
        category=category,
        category_label=CATEGORY_LABELS[category],
        plays=service.list_plays_for(category, current_user),
        editing=editing,
        # Carries the CSRF token on the Publish, Unpublish and Delete buttons.
        action_form=ConfirmActionForm() if editing else None,
    )


@playbook_bp.route("/plays/<int:play_id>")
@login_required
def play(play_id):
    play = service.get_play(play_id)
    # A draft looks exactly like a missing play to a player.
    if play is None or not service.can_view(play, current_user):
        abort(404)
    return render_template(
        "playbook/play.html",
        play=play,
        steps=service.steps_data(play),
        # The chat under the step text: today's messages and how many questions are left.
        assistant=assistant_service.panel(current_user, play),
    )
