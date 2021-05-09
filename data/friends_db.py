import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Friends(SqlAlchemyBase):
    __tablename__ = 'friends'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    friend_id = sqlalchemy.Column(sqlalchemy.Integer)
    user = orm.relation('User')
