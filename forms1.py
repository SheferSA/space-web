from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, RadioField, SelectField, PasswordField, BooleanField, TextAreaField
from wtforms.validators import DataRequired


class AddFriendsForm(FlaskForm):
    request_id = StringField('Номер запроса', validators=[DataRequired()])
    submit = SubmitField('Принять запрос')


class DeleteForm(FlaskForm):
    submit = SubmitField('Удалить профиль')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Отправить')


class ProfileForm(FlaskForm):
    submit = SubmitField('Опубликовать профиль')


class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    age = StringField('Возраст', validators=[DataRequired()])
    country = SelectField('Страна', choices=[
        ('Не задана', 'На задана'),
        ('Россия', 'Россия'),
        ('США', 'США'),
        ('Германия', 'Германия'),
        ('Китай', 'Китай')
    ], default='Не задана')
    sex = RadioField('Пол', choices=[('м', 'Мужской'), ('ж', 'Женский')], default='м')
    bio = TextAreaField('О себе', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    repeat_passw = PasswordField('Повторите пароль', validators=[DataRequired()])
    submit = SubmitField('Отправить')


class RequestForm(FlaskForm):
    profile_id = StringField('ID профиля', validators=[DataRequired()])
    submit = SubmitField('Отправить запрос')


class NotesForm(FlaskForm):
    header = StringField('Заголовок', validators=[DataRequired()])
    note = TextAreaField('Запись', validators=[DataRequired()])
    submit = SubmitField('Добавить запись')


class ParametersForm(FlaskForm):
    age_from = StringField('Возраст от...')
    age_to = StringField('Возраст до...')
    country = SelectField('Страна', choices=[
        ('Не задана', 'На задана'),
        ('Россия', 'Россия'),
        ('США', 'США'),
        ('Германия', 'Германия'),
        ('Китай', 'Китай')
    ], default='Не задана')
    sex = RadioField('Пол', choices=[('м', 'Мужской'), ('ж', 'Женский'), ('любой', 'Любой')], default='любой')
    submit = SubmitField('Отсортировать')
