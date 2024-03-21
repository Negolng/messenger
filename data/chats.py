from . import db_session
import sqlalchemy


class Chat(db_session.SqlAlchemyBase):
    __tablename__ = 'Chats'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False, unique=False, index=True)
