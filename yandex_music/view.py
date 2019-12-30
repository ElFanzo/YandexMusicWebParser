from flask import render_template

from . import app
from .exceptions import InternalServerError, PageNotFoundError


@app.route("/")
def index():
    """Represent a Home page."""
    return render_template("index.html")


@app.errorhandler(404)
@app.errorhandler(PageNotFoundError)
def page_not_found(error):
    if not isinstance(error, PageNotFoundError):
        error = PageNotFoundError()
    return render_template("error.html", error=error), error.code


@app.errorhandler(500)
def internal_error(error):
    return render_template("error.html", error=InternalServerError()), \
           error.code
