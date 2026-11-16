from flask import abort, render_template
from flask_login import current_user, login_required

from app.constants import CATEGORY_LABELS
from app.playbook import playbook_bp, service


@playbook_bp.route("/playbook")
@login_required
def index():
    return render_template("playbook/index.html", categories=service.list_categories())


@playbook_bp.route("/playbook/<slug>")
@login_required
def category(slug):
    category = service.find_category(slug)
    if category is None:
        abort(404)
    return render_template(
        "playbook/category.html",
        category_label=CATEGORY_LABELS[category],
        plays=service.list_published_plays(category),
    )


@playbook_bp.route("/plays/<int:play_id>")
@login_required
def play(play_id):
    play = service.get_play(play_id)
    # A draft looks exactly like a missing play to a player.
    if play is None or not service.can_view(play, current_user):
        abort(404)
    return render_template("playbook/play.html", play=play, steps=service.steps_data(play))
