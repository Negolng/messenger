from . import db_session
import sqlalchemy


class Message(db_session.SqlAlchemyBase):
    __tablename__ = 'Messages'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    message = sqlalchemy.Column(sqlalchemy.String, nullable=False, unique=False)
    date = sqlalchemy.Column(sqlalchemy.Integer, nullable=False, unique=False)
    author = sqlalchemy.Column(sqlalchemy.Integer, nullable=False, unique=False, index=True)
    chat = sqlalchemy.Column(sqlalchemy.Integer, nullable=False, unique=False)
