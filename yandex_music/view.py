from flask import render_template

from . import app


@app.route("/")
def index():
    """Represent a Home page."""
    return render_template("index.html")
