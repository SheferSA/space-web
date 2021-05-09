import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class Requests(SqlAlchemyBase):
    __tablename__ = 'requests'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    user_sender = sqlalchemy.Column(sqlalchemy.Integer,
                                    sqlalchemy.ForeignKey("users.id"))
    user_recipient = sqlalchemy.Column(sqlalchemy.Integer)

    user = orm.relation('User')
