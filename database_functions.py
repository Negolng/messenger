from data.users import User
from data import db_session
from hashlib import sha512
from string import digits, ascii_letters, punctuation, ascii_lowercase, ascii_uppercase
from data.chats import Chat
from data.user_chat import UserChat
from data.messages import Message


class MyTime:
    def __init__(self, year, day, hour, minute):
        self.year = year
        self.day = day
        self.hour = hour
        self.minute = minute

    def __str__(self):
        return f'{self.day}.{str(self.year)[2:]} {self.hour}:{self.minute}'


class PyMessage:
    def __init__(self, time: int, author: str, message: str):
        self.content = message
        self.author = author
        self.time = self.parse_time(time)

    @staticmethod
    def parse_time(time: int):
        year = time // (60 * 24 * 365) + 2024
        day = time // (60 * 24)
        hour = time // 60 % 24
        minute = time % 60
        dtime = MyTime(year, day, hour, minute)
        return dtime


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
    return (password and len(password) > 12 and
            all([all([letter in ascii_letters + digits + punctuation for letter in password]),
                sum([1 for letter in password if letter in ascii_lowercase]) >= 1,
                sum([1 for letter in password if letter in ascii_uppercase]) >= 1,
                sum([1 for letter in password if letter in digits]) >= 1,
                sum(1 for letter in password if letter in punctuation) >= 1]))


def validate_username(username: str) -> bool:
    return (username and all([letter in ascii_letters + digits + punctuation for letter in username])
            and 1 < len(username) < 64)


def validate_chatname(username: str) -> bool:
    return (username and all([letter in ascii_letters + digits + punctuation for letter in username])
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
    idd = chtid.id
    dbs.close()
    return idd


def add_users(users: list[str], chat_id: int, owner: str):
    dbs = db_session.create_session()
    for user in users:
        if user == owner:
            continue
        userid = dbs.query(User).filter(User.name == user)
        if not list(userid):
            dbs.close()
            dbs = db_session.create_session()
            dbs.delete(dbs.query(Chat).filter(Chat.id == chat_id)[0])
            dbs.delete(dbs.query(UserChat).filter(UserChat.chat_id == chat_id)[0])
            dbs.commit()
            dbs.close()
            return True, f'User with name {user} is not found'
        user_chat = UserChat()
        user_chat.user_id = userid[0].id
        user_chat.chat_id = chat_id
        dbs.add(user_chat)
    dbs.commit()
    dbs.close()
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
        all_users_with_access.append(dbs.query(User).filter(User.id == userid)[0])
    return all_users_with_access


def delete_acc(user: User):
    dbs = db_session.create_session()
    user_id: int = user.id
    # delete dependencies between the user and chats
    all_chats = dbs.query(UserChat).filter(UserChat.user_id == user_id)
    for chat in all_chats:
        dbs.delete(chat)
    dbs.delete(user)
    dbs.commit()
    dbs.close()


def get_chat_name(chat_id: int):
    dbs = db_session.create_session()
    chatname = dbs.query(Chat).filter(Chat.id == chat_id)
    if list(chatname):
        name = chatname[0].name
        dbs.close()
        return name
    return False


def get_messages(chat_id: int):
    dbs = db_session.create_session()
    messages = dbs.query(Message).filter(Message.chat == chat_id)
    rett = []
    for message in messages:
        math: int = message.author
        authname = dbs.query(User).filter(User.id == math)
        if not list(authname):
            return -1
        authname = authname[0].name
        rett.append(PyMessage(message.date, authname, message.message))
    dbs.close()
    return rett


def add_message(author: str, time: MyTime, message: str, chat: int):
    dbs = db_session.create_session()
    new_message = Message()
    new_message.message = message

    auth = dbs.query(User).filter(User.name == author)
    if not list(auth):
        return False, 'No such user'
    new_message.author = auth[0].id

    new_message.chat = chat

    mtime = (time.day * 24 * 60 +
             (time.year - 2024) * 365 * 24 * 60 +
             time.hour * 60 +
             time.minute)

    new_message.date = mtime
    dbs.add(new_message)
    dbs.commit()
    dbs.close()
    return True, ''
