from flask import render_template

from app.auth import auth_bp


@auth_bp.route("/", methods=["GET"])
def index():
    return render_template("auth/login.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    # Real sign-in arrives in Phase 1. For now the form just shows the page again.
    return render_template("auth/login.html")
