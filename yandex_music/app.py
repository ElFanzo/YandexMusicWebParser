from . import app, db
from . import models, view
from .users.blueprint import users


app.register_blueprint(users, url_prefix="/users")
