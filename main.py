from flask import Flask, render_template

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return render_template("login.html")

@app.route("/login", methods=["GET", "POST"])
def login():
<<<<<<< HEAD
    return render_template("login.html")    

if __name__ == "__main__":
    app.run(debug=True)
=======
    return render_template("login.html")
>>>>>>> 4b2baef22a3fea8c9aa7e3cc8478b038337af268
