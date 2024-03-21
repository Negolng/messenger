from flask import Flask, render_template, redirect, session, request
from secrets import randbits
from data import db_session
from login import LoginForm, login_required
from data.users import User
from data.messages import Message
from database_functions import *
from forms import ChatForm, ChangePasswordForm, DeleteAccountForm


app = Flask(__name__)
app.config['SECRET_KEY'] = str(randbits(128))


@app.before_request
def before():
    if 'logged_in' not in session.keys():
        session['logged_in'] = False
    if 'IP' not in session.keys():
        session['IP'] = request.remote_addr


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', session=session)


@app.route('/logout')
@login_required
def logout():
    session['logged_in'] = False
    return redirect('/')


@app.route('/reglogin', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.is_submitted():
        username: str = form.nickname.data
        password = form.password.data
        print(username, password)
        dbs = db_session.create_session()
        db_user = dbs.query(User).filter(User.name == username)
        dbs.close()
        if list(db_user):
            if db_user[0].password == hash_password(password):
                session['logged_in'] = True
                session['Username'] = username

                return redirect('/profile')
            else:
                return render_template('loginform.html', form=form, message='Incorrect password')
        result = registrate(username, password)
        if result:
            session['logged_in'] = True
            session['Username'] = username
            return redirect('/profile')
        else:
            return render_template('loginform.html', form=form, message='Invalid password or username')
    return render_template('loginform.html', form=form, message='')


@app.route('/profile')
@login_required
def profile():
    chats = find_chats(session['Username'])
    return render_template('profile.html', session=session, chats=chats)


@app.route('/profile/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()

    if form.is_submitted():
        old_password = form.old_password.data
        new_password = form.new_password.data
        if validate_password(new_password):
            dbs = db_session.create_session()
            username: str = session['Username']
            oldps: User = dbs.query(User).filter(User.name == username)[0]
            if oldps.password == hash_password(old_password):
                oldps.password = hash_password(new_password)
                dbs.commit()
                dbs.close()
                return redirect('/')
            return render_template('change_password.html', form=form,
                                   message='Wrong password')
        return render_template('change_password.html', form=form,
                               message='Invalid new password')

    return render_template('change_password.html', form=form)


@app.route('/profile/delete', methods=['GET', 'POST'])
@login_required
def delete_account():
    form = DeleteAccountForm()
    if form.is_submitted():
        passw = form.password.data
        dbs = db_session.create_session()
        username: str = session['Username']
        user: User = dbs.query(User).filter(User.name == username)[0]
        if user.password == hash_password(passw):
            dbs.close()
            delete_acc(user)
            session['logged_in'] = False
            session['Username'] = None
            return redirect('/')
        else:
            render_template("delete_account.html", form=form, message='Incorrect password!')
    return render_template("delete_account.html", form=form, message='')


@app.route('/profile/create_chat', methods=['GET', 'POST'])
@login_required
def create_chat():
    form = ChatForm()
    if form.is_submitted():
        if not validate_chatname(form.name.data):
            return render_template('create_chat.html', form=form, message="Invalid chat name")

        chat_id = add_chat(session['Username'], form.name.data)
        other_users = parse_users(form.users.data)
        if other_users:
            error, message = add_users(other_users, chat_id, session['Username'])
            if error:
                return render_template('create_chat.html', form=form, message=message)
        return redirect('/profile')
    return render_template('create_chat.html', form=form, message='')


@app.route('/chats/<int:chat_id>')
@login_required
def chat(chat_id):
    members: list[User] = find_users(chat_id)
    if members == -1:
        return "<p>Chat with such id doesn't exist</p>"
    all_names = [member.name for member in members]
    if session['Username'] not in all_names:
        return "<p>You don't have access to this chat</p>"
    return f'''
    
    <p>This is a chat with id: {chat_id}</p>
    <p>The members of this chat are: {', '.join(all_names)}</p>
    <h1>Work in progress!</h1>
    '''


def main():
    db_session.global_init("db/database.db")
    app.run()


if __name__ == '__main__':
    main()
