from data.users import User
from data import db_session
from hashlib import sha512


def hash_password(password: str):
    return sha512(password.encode()).hexdigest()


def add_user(nickname: str, password: str):
    user = User()
    user.name = nickname
    user.password = hash_password(password)
    session = db_session.create_session()
    session.add(user)
    session.commit()
