from flask import Flask, render_template, redirect
from forms1 import RegisterForm, LoginForm, ProfileForm, DeleteForm, \
    NotesForm, ParametersForm, AddFriendsForm, RequestForm
from flask_login import LoginManager, login_user, logout_user, current_user
from data import db_session, users, profiles, requests, friends_db, parameters, notes
import os

db_session.global_init("db/friends.sqlite")
session = db_session.create_session()
app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


def sort_profiles(parameter):  # сортируем анкеты по праметрам
    profiles_list_all = []
    profiles_list = []

    for profile in session.query(profiles.Profiles):
        profiles_list_all.append([profile, session.query(users.User).filter(
            users.User.id == profile.user_id).first()])  # получаем все анкеты

    if not parameter:  # если параметр сортировки не задан, то возвращаем полный список анкет
        return profiles_list_all

    for profile in profiles_list_all:  # если параметр задан
        user = profile[1]
        if ((parameter.age_from == '' or int(user.age) >= int(parameter.age_from))
                and (parameter.age_to == '' or int(user.age) <= int(parameter.age_to))
                and (parameter.country == 'Не задана' or user.country == parameter.country)):
               # and (parameter.sex == 'Любой' or user.sex == parameter.sex)):
            profiles_list.append(user)

    return profiles_list


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    form = RequestForm()

    if current_user.is_authenticated:  # проверим может ли быть установлен параметр поика
        parameter = session.query(parameters.Parameter).filter(parameters.Parameter.user_id == current_user.id).first()
    else:
        parameter = ''

    profiles_list = sort_profiles(parameter)  # получаем список анкет, подходящих под параметры

    if form.validate_on_submit():  # если запрос отправлен
        request = requests.Requests()

        if not current_user.is_authenticated:  # не можем отправить запрос если не известен отправитель
            return render_template('main.html', form=form,
                                   title="Главная",
                                   profs=profiles_list,
                                   message="Запрос не может быть отправлен"
                                   )

        try:  # пробуем получить анкету под введеным номером
            user_recipient = session.query(profiles.Profiles).filter(
                profiles.Profiles.id == form.profile_id.data).first().user_id
        except AttributeError:  # если не получается, значит анкеты не существует
            return render_template('main.html', form=form,
                                   title="Главная",
                                   profs=profiles_list,
                                   message="Такого профиля не существует")

        if current_user.id != user_recipient:  # проверяем, чтобы запрос не отправить самому себе
            for request in session.query(requests.Requests):
                if [request.user_sender, request.user_recipient] == [current_user.id,
                                                                     user_recipient]:  # если запрос уже отправлен
                    return render_template('main.html', form=form,
                                           title="Главная",
                                           profs=profiles_list,
                                           message="Запрос уже отправлен")

            for friend in session.query(friends_db.Friends).filter(friends_db.Friends.user_id == current_user.id):
                if friend.friend_id == session.query(profiles.Profiles).filter(
                        profiles.Profiles.id == form.profile_id.data).first().user_id:  # если уже в друзьях
                    return render_template('main.html', form=form,
                                           title="Главная",
                                           profs=profiles_list,
                                           message="Пользователь уже в друзьях")

            for request in session.query(requests.Requests).filter(requests.Requests.user_recipient == current_user.id):
                if request.user_sender == session.query(profiles.Profiles).filter(
                        profiles.Profiles.id == form.profile_id.data).first().user_id:
                    # нам уже отправил запрос этот пользователь
                    return render_template('main.html', form=form,
                                           title="Главная",
                                           profs=profiles_list,
                                           message="Проверь свои запросы")

            request.user_sender = current_user.id
            request.user_recipient = user_recipient
            session.add(request)
            session.commit()
            return render_template('main.html', form=form,
                                   title="Главная",
                                   profs=profiles_list)
        return render_template('main.html', form=form,
                               title="Главная",
                               profs=profiles_list,
                               message="Запрос не может быть отправлен"
                               )
    return render_template('main.html', title='Главная',
                           profs=profiles_list, form=form)


@app.route('/friends/requests', methods=['GET', 'POST'])
def friends_requests():  # принять запрс в друзья
    form = AddFriendsForm()
    requests_list = []
    for request in session.query(requests.Requests).filter(requests.Requests.user_recipient == current_user.id):
        requests_list.append(
            [request.id, session.query(users.User).filter(users.User.id == request.user_sender).first()])
        # все запросы текущего пользователя
    if form.validate_on_submit():
        friend = friends_db.Friends()
        friend.user_id = current_user.id
        try:  # проверяем есть ли анкета под таким номером
            friend.friend_id = session.query(requests.Requests).filter(
                requests.Requests.id == form.request_id.data).first().user_sender
        except AttributeError:
            return render_template('requests.html',
                                   title="Запросы", form=form,
                                   requests_list=requests_list, message='Запрос не существует')
        session.add(friend)
        session.delete(session.query(requests.Requests).filter(
            requests.Requests.id == form.request_id.data).first())  # удаляем запрос
        session.commit()
        requests_list = []  # обновляем список запросов
        for request in session.query(requests.Requests).filter(requests.Requests.user_recipient == current_user.id):
            if type(request) != 'NoneType':  # если не осталось запросов
                requests_list.append(
                    [request.id, session.query(users.User).filter(users.User.id == request.user_sender).first()])
        return render_template('requests.html',
                               title="Запросы", form=form,
                               requests_list=requests_list)
    return render_template('requests.html',
                           title="Запросы", form=form,
                           requests_list=requests_list)


@app.route('/friends', methods=['GET', 'POST'])
def friends():
    friends_list = []
    form = ProfileForm()
    form_delete = DeleteForm()
    profs_list = []

    if not current_user.is_authenticated:
        return render_template('friends.html',
                               title="Друзья")

    for friend in session.query(friends_db.Friends).filter(
            friends_db.Friends.user_id == current_user.id):  # список друзей
        friends_list.append(session.query(users.User).filter(users.User.id == friend.friend_id).first())

    for profile in session.query(profiles.Profiles):
        profs_list.append(profile.user_id)

    if form.validate_on_submit() and current_user.id not in profs_list:  # если анкета не опубликована
        profile = profiles.Profiles()
        profile.user_id = current_user.id
        session.add(profile)
        session.commit()
        profs_list = []  # обновляем список анкет
        for profile in session.query(profiles.Profiles):
            profs_list.append(profile.user_id)
    elif form_delete.validate_on_submit() and current_user.id in profs_list:  # если анкета опубликована
        session.delete(session.query(profiles.Profiles).filter(profiles.Profiles.user_id == current_user.id).first())
        session.commit()
        profs_list = []  # обновляем список анкет
        for profile in session.query(profiles.Profiles):
            profs_list.append(profile.user_id)
    return render_template('friends.html', form=form,
                           title="Друзья", profs=profs_list,
                           user_id=current_user.id, form_delete=form_delete,
                           friends=friends_list)


@app.route('/login', methods=['GET', 'POST'])
def sign_in():  # вход
    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(users.User).filter(users.User.email == form.email.data).first()
        if user and (user.password == form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('sign_in.html',
                               title="Вход",
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('sign_in.html', form=form, title='Вход')


@app.route('/logout')
def logout():  # выход
    logout_user()
    return redirect("/")


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(users.User).get(user_id)


@app.route('/register', methods=['GET', 'POST'])
def register():  # регистрация
    form = RegisterForm()
    if form.validate_on_submit():
        user = users.User()
        user.name = form.name.data
        user.surname = form.surname.data
        user.age = form.age.data
        user.country = form.country.data
        user.sex = form.sex.data
        user.password = form.password.data
        user.email = form.email.data
        user.bio = form.bio.data
        if session.query(users.User).filter(users.User.email == form.email.data).first():
            return render_template('reg.html', form=form, title="Регистрация", message="Email уже зарегистрирован.")
        if int(form.age.data) <= 0:  # проверяем корректность возраста
            return render_template('reg.html', form=form, title="Регистрация", message="Некорректный возраст.")
        if len(form.password.data) < 4:  # проверяем корректность пароля
            return render_template('reg.html', form=form, title="Регистрация", message="Слишком короткий пароль")
        if form.password.data != form.repeat_passw.data:  # сравниваем пароли
            return render_template('reg.html', form=form, message="Пароли должны совпадать!", title="Регистрация")
        else:
            session.add(user)
            session.commit()
            return render_template('reg.html', form=form, message="Регистрация успешна!", title="Регистрация")
    else:
        return render_template('reg.html', form=form, title="Регистрация")


@app.route('/notes', methods=['GET', 'POST'])
def notes_func():  # добавляем заметки
    form = NotesForm()
    notes_list = []
    if current_user.is_authenticated:
        for note in session.query(notes.Note).filter(notes.Note.user_id == current_user.id):
            notes_list.append(note)  # заметки текущего пользователя
    if form.validate_on_submit():
        note = notes.Note()
        note.user_id = current_user.id
        note.header = form.header.data
        note.note = form.note.data
        session.add(note)
        session.commit()
        notes_list = []  # обновляем список заметок
        for note in session.query(notes.Note).filter(notes.Note.user_id == current_user.id):
            notes_list.append(note)
    return render_template('notes.html', title="Заметки", form=form,
                           notes=notes_list)


@app.route('/parameters', methods=['GET', 'POST'])
def parameters_func():  # ставим параметры поиска
    form = ParametersForm()
    if form.validate_on_submit():
        if ((form.age_from.data and int(form.age_from.data) <= 0)
                or (form.age_to.data and int(form.age_to.data) <= 0)
                or (form.age_from.data and form.age_to.data and
                    int(form.age_from.data) > int(form.age_to.data))):
            return render_template('parameters.html', title="Поиск",
                                   form=form, message='Некорректный возраст')  # проверяем возраст на корректность
        for parameter in session.query(parameters.Parameter).filter(parameters.Parameter.user_id == current_user.id):
            session.delete(parameter)  # очищаем бд с параметрами, чтобы не было накладок
        parameter = parameters.Parameter()
        parameter.user_id = current_user.id
        parameter.age_from = form.age_from.data
        parameter.age_to = form.age_to.data
        parameter.country = form.country.data
        parameter.sex = form.sex.data
        session.add(parameter)
        session.commit()
    return render_template('parameters.html', title="Поиск по параметрам",
                           form=form)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(port=port, host='0.0.0.0')
    # app.run(port=8083, host='127.0.0.1', debug=True)
