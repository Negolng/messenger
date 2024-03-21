from data.users import User
from data import db_session
from hashlib import sha512
from string import digits, ascii_letters, punctuation, ascii_lowercase, ascii_uppercase
from data.chats import Chat
from data.user_chat import UserChat


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


def validate_chatname(username: str) -> bool:
    return (all([letter in ascii_letters + digits + punctuation for letter in username])
            and 1 < len(username) < 64)


def add_chat(username: str, chatname: str) -> int:
    dbs = db_session.create_session()

    # create all basic objects
    chat = Chat()
    user_chat = UserChat()

    user = dbs.query(User).filter(User.name == username)[0]

    user_chat.user_id = user.id

    chat.name = chatname
    dbs.add(chat)
    dbs.commit()

    chtid: Chat = dbs.query(Chat).filter(Chat.name == chat.name)[0]
    user_chat.chat_id = chtid.id
    dbs.add(user_chat)

    dbs.commit()
    return chtid.id


def add_users(users: list[str], chat_id: int):
    dbs = db_session.create_session()
    for user in users:
        userid = dbs.query(User).filter(User.name == user)
        if not list(userid):
            dbs.close()
            dbs = db_session.create_session()
            dbs.delete(dbs.query(Chat).filter(Chat.id == chat_id)[0])
            dbs.delete(dbs.query(UserChat).filter(UserChat.chat_id == chat_id)[0])
            dbs.commit()
            return True, f'User with name {user} is not found'
        user_chat = UserChat()
        user_chat.user_id = userid[0].id
        user_chat.chat_id = chat_id
        dbs.add(user_chat)
    dbs.commit()
    return False, ''


def parse_users(users: str):
    return users.split()


def find_chats(username: str):
    dbs = db_session.create_session()
    user_id: int = dbs.query(User).filter(User.name == username)[0].id
    chats = dbs.query(UserChat).filter(UserChat.user_id == user_id)
    chatnames = []
    for chat in chats:
        chatid: int = chat.chat_id
        chatnames.append(dbs.query(Chat).filter(Chat.id == chatid)[0])
    return chatnames


def find_users(chat_id: int):
    dbs = db_session.create_session()
    all_users_with_access = []
    user_ids = dbs.query(UserChat).filter(UserChat.chat_id == chat_id)
    if not list(user_ids):
        return -1
    for user in user_ids:
        userid: int = user.user_id
        # TODO: Когда пользователь удаляет аккаунт, также удалить  его из всех чатов, иначе программа сломается
        all_users_with_access.append(dbs.query(User).filter(User.id == userid)[0])
    return all_users_with_access
