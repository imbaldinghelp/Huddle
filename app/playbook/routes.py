from flask import abort, redirect, render_template, url_for
from flask_login import current_user, login_required

from app.assistant import service as assistant_service
from app.assistant.forms import AskForm
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


# The play page shows the diagram and, under it, a box for asking the
# assistant about this play. Asking posts back to the same address.
@playbook_bp.route("/plays/<int:play_id>", methods=["GET", "POST"])
@login_required
def play(play_id):
    play = service.get_play(play_id)
    # A draft looks exactly like a missing play to a player.
    if play is None or not service.can_view(play, current_user):
        abort(404)

    form = AskForm()
    error = None
    if form.validate_on_submit():
        # Drafts are not part of the playbook, so there is nothing to ask about.
        if not play.is_published:
            abort(404)
        try:
            assistant_service.ask(current_user, form.question.data, play)
        except assistant_service.AssistantError as problem:
            error = str(problem)
        else:
            # Redirect so refreshing the page does not ask the question again.
            # "#answers" scrolls down to the new answer.
            return redirect(url_for("playbook.play", play_id=play.id, _anchor="answers"))

    return render_template(
        "playbook/play.html",
        play=play,
        steps=service.steps_data(play),
        form=form,
        error=error,
        assistant=assistant_service.panel(current_user, play),
    )
