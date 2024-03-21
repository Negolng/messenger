from . import db_session
import sqlalchemy


class UserChat(db_session.SqlAlchemyBase):
    __tablename__ = 'UserChats'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=False, unique=False)
    chat_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=False, unique=False)
