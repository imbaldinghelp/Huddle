from flask import current_app, flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app.assistant import service as assistant_service
from app.auth import auth_bp, service
from app.auth.forms import ChangePasswordForm, LoginForm, SetPasswordForm
from app.extensions import limiter


def safe_next_url():
    """Return the page the user was trying to open, if it is inside Huddle.

    Only local paths are accepted so a crafted link cannot bounce someone to
    another website after they log in.
    """
    target = request.args.get("next", "")
    if target.startswith("/") and not target.startswith("//") and "\\" not in target:
        return target
    return None


@auth_bp.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("playbook.index"))
    return redirect(url_for("auth.login"))


@auth_bp.route("/login", methods=["GET", "POST"])
@limiter.limit(lambda: current_app.config["LOGIN_RATE_LIMIT"], methods=["POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("playbook.index"))

    form = LoginForm()
    error = None
    if form.validate_on_submit():
        user, error = service.authenticate(form.username.data, form.password.data)
        if user is not None:
            login_user(user)
            # "Permanent" means the cookie lasts PERMANENT_SESSION_LIFETIME
            # instead of ending when the browser closes.
            session.permanent = True
            service.record_login(user)
            return redirect(safe_next_url() or url_for("playbook.index"))
    return render_template("auth/login.html", form=form, error=error)


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))


# Clicking your name in the header opens this page.
@auth_bp.route("/account")
@login_required
def account():
    return render_template(
        "auth/account.html", questions_left=assistant_service.questions_left(current_user)
    )


@auth_bp.route("/account/password", methods=["GET", "POST"])
@login_required
def change_password():
    forced = current_user.must_change_password
    form = SetPasswordForm() if forced else ChangePasswordForm()
    if form.validate_on_submit():
        service.change_password(current_user, form.new_password.data)
        flash("Your password has been changed.", "success")
        # A first-time password opens the playbook; a chosen change goes back to the account page.
        return redirect(url_for("playbook.index" if forced else "auth.account"))
    return render_template("auth/change_password.html", form=form, forced=forced)
