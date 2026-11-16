from flask import render_template
from flask_login import login_required

from app.playbook import playbook_bp


@playbook_bp.route("/playbook")
@login_required
def index():
    # The category cards and plays arrive in Phase 2.
    return render_template("playbook/index.html")
