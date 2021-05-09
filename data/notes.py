import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Note(SqlAlchemyBase):
    __tablename__ = 'notes'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    note = sqlalchemy.Column(sqlalchemy.String)
    header = sqlalchemy.Column(sqlalchemy.String)

    user = orm.relation('User')
