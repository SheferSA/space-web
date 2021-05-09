import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm
from flask_login import UserMixin


class Parameter(SqlAlchemyBase, UserMixin):
    __tablename__ = 'parameters'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    age_from = sqlalchemy.Column(sqlalchemy.Integer)
    age_to = sqlalchemy.Column(sqlalchemy.Integer)
    country = sqlalchemy.Column(sqlalchemy.String)

    user = orm.relation('User')
