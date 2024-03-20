from flask import Flask, render_template, redirect, session, request
from secrets import randbits
from data import db_session
from login import LoginForm, login_required
from data.users import User
from database_functions import hash_password, registrate, validate_chatname, validate_password
from forms import ChatForm, ChangePasswordForm


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
    return render_template('index.html')


@app.route('/logout')
@login_required
def logout():
    session['logged_in'] = False
    return redirect('/')


@app.route('/reglogin', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.is_submitted():
        username = form.nickname.data
        password = form.password.data
        print(username, password)
        dbs = db_session.create_session()
        db_user = dbs.query(User).filter(User.name == username)
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
    return render_template('profile.html', session=session)


@app.route('/profile/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()

    if form.is_submitted():
        old_password = form.old_password.data
        new_password = form.new_password.data
        if validate_password(new_password):
            dbs = db_session.create_session()
            username = session['Username']
            oldps: User = dbs.query(User).filter(User.name == username)[0]
            if oldps.password == hash_password(old_password):
                oldps.password = hash_password(new_password)
                dbs.commit()
                return redirect('/')
            return render_template('change_password.html', form=form,
                                   message='Wrong password')
        return render_template('change_password.html', form=form,
                               message='Invalid new password')

    return render_template('change_password.html', form=form)


@app.route('/profile/create_chat', methods=['GET', 'POST'])
@login_required
def create_chat():
    form = ChatForm()
    if form.is_submitted():
        if not validate_chatname(form.name.data):
            return render_template('create_chat.html', form=form, message="Invalid chat name")
        
        return render_template('create_chat.html', form=form, message="Chat hasn't been created")
    return render_template('create_chat.html', form=form, message='')


def main():
    db_session.global_init("db/Users.db")
    # add_user('Negolng', 'PipaVPope')
    # add_user('popa', 'pipa')
    app.run()


if __name__ == '__main__':
    main()
