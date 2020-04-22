# -- coding: utf-8 --
from flask import Flask, render_template, redirect, request, abort, make_response, jsonify
from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired
from data import db_session
from data.user import User
from data.organization import Organization
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import os

app = Flask(__name__, template_folder='templates')

app.config['SECRET_KEY'] = 'artemovnavar2@gmail.com'
login_manager = LoginManager()
login_manager.init_app(app)


class RegisterForm(FlaskForm):
    email = StringField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    position = StringField('Позиция', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')


class AddOrganizationForm(FlaskForm):
    organization_name = StringField('Наименование компании', validators=[DataRequired()])
    address = StringField('Адрес', validators=[DataRequired()])
    description = StringField('Описание компании', validators=[DataRequired()])
    contact_number = StringField('Контактный номер', validators=[DataRequired()])
    file = FileField('Загрузите логотип организации', validators=[DataRequired()])
    submit = SubmitField('Подать заявку')


class LoginForm(FlaskForm):
    email = StringField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


@app.route('/')
def test():
    db_session.global_init("db/blogs.sqlite")
    session = db_session.create_session()
    return render_template('test.html', title='Main', items=session.query(Organization).all())

@app.route('/organizations')
def base():
    db_session.global_init("db/blogs.sqlite")
    session = db_session.create_session()
    return render_template('main.html', title='Main', items=session.query(Organization).all())


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('user_registration.html', title='Регистрация', form=form,
                                   message="Пароли не совпадают")
        session = db_session.create_session()
        if session.query(User).filter(User.email == form.email.data).first():
            return render_template('user_registration.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            email=form.email.data,
            name=form.name.data,
            surname=form.surname.data,
            position=form.position.data,
        )
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        return redirect('/login')
    return render_template('user_registration.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('user_login.html', message="Неправильный логин или пароль", form=form)
    return render_template('user_login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.route('/addorganization', methods=['GET', 'POST'])
@login_required
def addorganization():
    form = AddOrganizationForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        organization = Organization(
            organization_name=form.organization_name.data,
            address=form.address.data,
            description=form.description.data,
            contact_number=form.contact_number.data,
        )
        organization.logo = organization.organization_name + '.' + request.files['file'].filename.split('.')[-1]
        request.files['file'].save(os.path.join(os.getcwd() + '/static/img', organization.logo))

        print(organization.logo)

        organization.set_address_ll()
        organization.owner_id = current_user.id
        current_user.organizations.append(organization)
        session.merge(current_user)
        session.commit()
        return redirect('/')
    return render_template('addorganization.html', title='Добавление организации', form=form)


@app.route('/organizations/<int:org_id>', methods=['GET', 'POST'])
def organization_id(org_id):
    session = db_session.create_session()
    organization = session.query(Organization).get(org_id)

    return render_template('organization.html',
                           title=organization.organization_name,
                           item=organization)


@app.route('/deleteorganization/<int:org_id>', methods=['GET', 'POST'])
@login_required
def organization_delete(org_id):
    session = db_session.create_session()
    if current_user.id == 1:
        organization = session.query(Organization).filter(Organization.id == org_id).first()
    else:
        organization = session.query(Organization).filter(Organization.id == org_id,
                                                          Organization.owner == current_user).first()
    if organization:
        session.delete(organization)
        session.commit()
    else:
        abort(404)
    return redirect('/')


def main():
    db_session.global_init("db/blogs.sqlite")
    app.run()


if __name__ == '__main__':
    main()
