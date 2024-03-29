from wtforms import StringField, SubmitField, PasswordField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired


class ChatForm(FlaskForm):
    name = StringField("Chat's name", validators=[DataRequired()])
    users = StringField()
    submit = SubmitField("Submit")


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Old password', validators=[DataRequired()])
    new_password = PasswordField('New password', validators=[DataRequired()])
    submit = SubmitField('Submit')


class MessageForm(FlaskForm):
    message_field = StringField("Your message", validators=[DataRequired()])
    send = SubmitField("Send")


class DeleteAccountForm(FlaskForm):
    password = StringField('Enter your password before deleting the account', validators=[DataRequired()])
    submit = SubmitField("Delete my account")


class DeleteChatForm(FlaskForm):
    delete = SubmitField("Delete the chat")
