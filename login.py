from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm
from flask import session, render_template


session: session


class LoginForm(FlaskForm):
    nickname = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Submit')


def login_required(function):
    def _fuck(*args, **kwargs):
        if session['logged_in']:
            return function(*args, **kwargs)
        return render_template('no_login.html')

    _fuck.__name__ = function.__name__
    return _fuck
