from . import db_session
import sqlalchemy


class User(db_session.SqlAlchemyBase):
    __tablename__ = 'users'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False, unique=True, index=True)
    password = sqlalchemy.Column(sqlalchemy.String, nullable=False, unique=False)
