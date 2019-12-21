from . import app, db
from . import models, view
from . import users


app.register_blueprint(users, url_prefix="/users")
