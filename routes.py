from flask import Flask, render_template, redirect, session, request, jsonify
from secrets import randbits
from login import LoginForm, login_required
from database_functions import *
from forms import *
import datetime as dt

app = Flask(__name__)
app.config['SECRET_KEY'] = str(randbits(128))

gl_token = int(randbits(32))


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


@app.route('/chats/<int:chat_id>', methods=["GET", 'POST'])
@login_required
def chat(chat_id):
    members: list[User] = find_users(chat_id)

    if members == -1:
        return "<p>Chat with such id doesn't exist</p>"

    # check if this chat exists
    chatname = get_chat_name(chat_id)
    all_names = [member.name for member in members]

    if session['Username'] not in all_names:
        return "<p>You don't have access to this chat</p>"

    form = MessageForm()
    messages = get_messages(chat_id)
    if form.is_submitted():
        if form.message_field.data:
            moment = dt.datetime.now()
            add_message(session['Username'], MyTime(int(moment.year), int(moment.day), int(moment.hour),
                                                    int(moment.minute)), form.message_field.data, chat_id)
            return redirect(f'/chats/{chat_id}')
    return render_template('chat.html', form=form, chatname=chatname, messages=messages, members=', '.join(all_names),
                           chat_id=chat_id, token=gl_token)


@app.route('/chats/<int:chat_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_chat_route(chat_id):

    members: list[User] = find_users(chat_id)

    if members == -1:
        return "<p>Chat with such id doesn't exist</p>"
    chatname = get_chat_name(chat_id)

    # check if this chat exists
    all_names = [member.name for member in members]

    if session['Username'] not in all_names:
        return "<p>You don't have access to this chat</p>"

    form = DeleteChatForm()
    if form.is_submitted():
        delete_chat(chat_id)
        return redirect('/profile')
    return render_template('delete_chat.html', form=form, chatname=chatname)


@app.route('/api/get_messages/<int:chat_id>/<int:token>')
def get_messages_t(chat_id, token):
    if token == token:
        respns = {'messages': []}
        messages = get_messages(chat_id)
        for message in messages:
            respns['messages'].append({'author': message.author,
                                       'time': {'years': message.time.year,
                                                'days': message.time.day,
                                                'hours': message.time.hour,
                                                'minutes': message.time.minute},
                                       'message_content': message.content})
        return jsonify(respns)

    else:
        return 'Sorry, but you cannot access this page without a token'


def main():
    from waitress import serve
    db_session.global_init("db/database.db")
    serve(app, host="127.0.0.1", port=8080)
    # app.run(port=8080)


if __name__ == '__main__':
    main()
