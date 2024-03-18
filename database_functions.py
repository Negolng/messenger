from data.users import User
from data import db_session
from hashlib import sha512
from string import digits, ascii_letters, punctuation, ascii_lowercase, ascii_uppercase


def hash_password(password: str) -> str:
    return sha512(password.encode()).hexdigest()


def add_user(nickname: str, password: str):
    user = User()
    user.name = nickname
    user.password = hash_password(password)
    session = db_session.create_session()
    session.add(user)
    session.commit()


def registrate(username: str, password: str) -> bool:
    if validate_password(password) and validate_username(username):
        add_user(username, password)
        return True
    else:
        return False


def validate_password(password: str) -> bool:
    return (len(password) > 12 and
            all([all([letter in ascii_letters + digits + punctuation for letter in password]),
                sum([1 for letter in password if letter in ascii_lowercase]) >= 1,
                sum([1 for letter in password if letter in ascii_uppercase]) >= 1,
                sum([1 for letter in password if letter in digits]) >= 1,
                sum(1 for letter in password if letter in punctuation) >= 1]))


def validate_username(username: str) -> bool:
    return (all([letter in ascii_letters + digits + punctuation for letter in username])
            and 1 < len(username) < 64)
