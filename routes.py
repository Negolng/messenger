from flask import Flask, render_template, redirect, session, request, make_response
from secrets import randbits
from data import db_session
from login import LoginForm, login_required
from data.users import User
from database_functions import hash_password, registrate


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
                return redirect('/')
            else:
                return render_template('loginform.html', form=form, message='Incorrect password')
        result = registrate(username, password)
        if result:
            session['logged_in'] = True
            session['Username'] = username
            return redirect('/')
        else:
            return render_template('loginform.html', form=form, message='Invalid password or username')
    return render_template('loginform.html', form=form, message='')


@app.route('/info')
@login_required
def profile():
    return render_template('profile.html', session=session)


def main():
    db_session.global_init("db/Users.db")
    # add_user('Negolng', 'PipaVPope')
    # add_user('popa', 'pipa')
    app.run()


if __name__ == '__main__':
    main()
