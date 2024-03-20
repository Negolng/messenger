from wtforms import StringField, SubmitField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired


class ChatForm(FlaskForm):
    name = StringField("Chat's name", validators=[DataRequired()])
    users = StringField()
    submit = SubmitField("Submit")
