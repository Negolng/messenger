from flask import Flask, render_template, redirect
from secrets import randbits
from data import db_session
from login import LoginForm
from data.users import User
from flask_login import login_user, LoginManager
from database_functions import hash_password, add_user


app = Flask(__name__)
app.config['SECRET_KEY'] = str(randbits(128))

manager = LoginManager()
manager.init_app(app)


@manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/reglogin', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        return redirect('/index')
        # return render_template('loginform.html', form=form, message="Account created")
    return render_template('loginform.html', form=form, message="anus")


def main():
    db_session.global_init("db/Users.db")
    # add_user('Negolng', 'PipaVPope')
    app.run()


if __name__ == '__main__':
    main()
