import re

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, ValidationError

from .models import User
from .network import Connection


def login_check(form, login):
    value = login.data.strip().lower()

    if not value:
        raise ValidationError

    login.data = re.sub(r"@ya\w{,4}\.\w{,3}", "", value)

    if User.query.filter_by(login=value).first():
        raise ValidationError(f"The user '{value}' already exists.")

    js = Connection().get_json("info", value)

    access = js.get("visibility")
    if not access:
        raise ValidationError(f"The user '{value}' does not exist.")

    if access != "public":
        raise ValidationError(f"The user '{value}' profile is private!")

    if not js["hasTracks"]:
        raise ValidationError(f"The user '{value}' has no tracks yet!")


class UserForm(FlaskForm):
    login = StringField(
        "The Yandex account login",
        validators=[DataRequired(), login_check]
    )
    submit = SubmitField("+ Add user")
