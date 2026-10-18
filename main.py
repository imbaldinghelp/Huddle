from flask import Flask, render_template

app = Flask(__name__)

@app.get("/")
def index():
    return render_template("login.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    return render_template("login.html")
