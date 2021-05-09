import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Profiles(SqlAlchemyBase):
    __tablename__ = 'profiles'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    user = orm.relation('User')
