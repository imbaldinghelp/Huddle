"""Friendly error pages instead of the browser's default ones."""

from flask import render_template

from app.extensions import db

TOO_MANY_LOGINS_MESSAGE = "Too many login attempts. Wait a minute, then try again."


def register_error_handlers(app):
    @app.errorhandler(403)
    def forbidden(error):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(error):
        # Undo any half-finished database work so the next request starts clean.
        db.session.rollback()
        return render_template("errors/500.html"), 500

    @app.errorhandler(400)
    def bad_request(error):
        # Usually a form left open so long that its security (CSRF) token expired.
        return render_template("errors/400.html"), 400

    @app.errorhandler(429)
    def too_many_requests(error):
        # Only the login form is rate limited, so show the message there.
        from app.auth.forms import LoginForm

        page = render_template("auth/login.html", form=LoginForm(), error=TOO_MANY_LOGINS_MESSAGE)
        return page, 429
