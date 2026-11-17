from flask import abort, jsonify, request
from flask_login import current_user, login_required

from app.assistant import assistant_bp, service
from app.playbook import service as play_service


# The chat on the play page sends each question here with JavaScript, as JSON
# (with the CSRF token in a header), and gets the answer back as JSON.
@assistant_bp.route("/plays/<int:play_id>/ask", methods=["POST"])
@login_required
def ask(play_id):
    play = play_service.get_play(play_id)
    # Drafts are not part of the playbook, so there is nothing to ask about.
    if play is None or not play.is_published:
        abort(404)

    data = request.get_json(silent=True) or {}
    try:
        chat = service.ask(current_user, data.get("question"), play)
    except service.AssistantError as problem:
        return jsonify(error=str(problem), **left_today()), 400
    return jsonify(answer=chat.answer, **left_today())


def left_today():
    """How many questions remain, so the page can update its count."""
    return {
        "questions_left": service.questions_left(current_user),
        "limit_message": service.daily_limit_message(),
    }
