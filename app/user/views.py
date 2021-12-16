import os
import secrets
from datetime import timedelta

from PIL import Image
from flask import render_template, redirect, url_for, flash, request, \
    current_app, session, jsonify
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
from app import db, bcrypt, mail, login_manager
from app.user.models import Post, Comment
from . import user_bp
from .models import User
from .forms import LoginForm, RegistrationForm, AccountUpdateForm,\
    PasswordUpdateForm, ResetPasswordForm, RequestPasswordResetForm
from app.utils import handle_posts_view
import cloudinary
import cloudinary.uploader
from io import BytesIO


def save_picture(form_picture):
    output_size = (800, 800)
    im = Image.open(form_picture)
    im.thumbnail(output_size)
    buf = BytesIO()
    # зберігаємо об'єкт Image в об'єкт BytesIO
    im.save(buf, 'png')
    buf.seek(0)
    image_bytes = buf.read()
    buf.close()
    upload_result = cloudinary.uploader.upload(
        image_bytes, folder=current_app.config['IMG_STORAGE_FOLDER'])
    return upload_result.get("url").split(
        current_app.config['IMG_STORAGE_FOLDER']+'/')[1]


# @login_manager.unauthorized_handler
# def unauthorized_callback():
#     flash('Авторизуйтесь, щоб отримати доступ', 'info')
#     return redirect(url_for('user_bp_in.login'))


@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user_in_db = User.query.filter_by(email=form.email.data).first()

        if user_in_db:
            if user_in_db.verify_password(form.password.data):
                login_user(user_in_db, remember=form.remember.data)
                session.permanent = True
                current_app.permanent_session_lifetime = timedelta(hours=3)
                flash(f'Користувач успішно увійшов у свій аккаунт!', 'success')
                next_page = request.args.get('next')
                # print('next post', next_page)
                if next_page:
                    return redirect(next_page)
                return redirect(url_for('user_bp_in.account'))
            else:
                flash('Введено невірний пароль.', 'danger')
                return redirect(url_for('user_bp_in.login'))
        else:
            flash('Користувач із вказаним емейлом не зареєстрований на сайті.',
                  'danger')

    return render_template('login.html', form=form, title='Login')


@user_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        # print(form.username.data, form.email.data, form.password.data)
        user = User(username=form.username.data, email=form.email.data,
                    password=form.password.data)
        try:
            db.session.add(user)
            db.session.commit()
            flash(f'Користувач {form.username.data} успішно зареєстрований!',
                  'success')
        except:
            db.session.rollback()
            flash('Трапилась помилка під час реєстрації корисутвача, '
                  'спробуйте ще раз.', 'danger')
        return redirect(url_for('user_bp_in.login'))
    return render_template('register.html', form=form, title='Register')


@user_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Ви вийшли зі свого облікового запису', 'info')
    return redirect(url_for('user_bp_in.login'))


@user_bp.route("/account")
@login_required
def account():
    posts = Post.query.filter_by(user_id=current_user.id)
    posts, sort_by = handle_posts_view(posts,
                                       request.args)

    # коментарі до постів ПОТОЧНОНО користувача і НЕ написані поточним
    # користувачем
    comments = db.session.query(Comment).join(Post). \
        filter(Comment.post_id == Post.id,
               Comment.user_id != current_user.id,
               Post.user_id == current_user.id). \
        order_by(Comment.created_at.desc())

    return render_template('account.html', posts=posts, sort_by=sort_by,
                           liked_posts=current_user.get_liked_posts(),
                           comments=comments)


@user_bp.route("/account/update", methods=['GET', 'POST'])
@login_required
def account_update():
    form_account = AccountUpdateForm()
    form_password = PasswordUpdateForm()
    if request.method == 'GET':
        form_account.username.data = current_user.username
    elif form_account.validate_on_submit():
        if form_account.picture.data:
            picture_file = save_picture(form_account.picture.data)
            current_user.picture = picture_file
        current_user.username = form_account.username.data
        try:
            db.session.commit()
            flash('Дані успішно оновлено', 'info')
            return redirect(url_for('user_bp_in.account'))
        except:
            db.session.rollback()
            flash('Помилка при оновленні даних', 'danger')
            return redirect(url_for('user_bp_in.account_update'))
    return render_template('account_update.html', form_account=form_account,
                           form_password=form_password)


@user_bp.route("/account/update/password", methods=['GET', 'POST'])
@login_required
def password_update():
    form_password = PasswordUpdateForm()
    form_account = AccountUpdateForm()
    if form_password.validate_on_submit():
        if current_user.verify_password(form_password.old_password.data):
            send_reset_token_to_email(current_user)
            flash('Лист з посиланням на відновлення паролю було надіслано на '
                  'вашу пошту', 'info')
            return redirect(url_for('user_bp_in.account'))
        else:
            flash('Неправильний старий пароль', 'danger')
            return redirect(url_for('user_bp_in.account_update'))
    else:
        form_account.username.data = current_user.username
        return render_template('account_update.html',
                               form_account=form_account,
                               form_password=form_password)


def send_reset_token_to_email(user):
    token = user.get_reset_token()
    msg = Message('Запит на скидання паролю',
                  sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f'''Щоб скинути пароль, перейдіть за наступним посиланням:
{url_for('user_bp_in.reset_password', token=token, _external=True)}
Якщо ви не подавали запит на зміну паролю - проігноруйте дане повідомлення'''
    mail.send(msg)


@user_bp.route("/reset_password", methods=['GET', 'POST'])
def request_password_reset():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestPasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_token_to_email(user)
        flash('Лист з посиланням на відновлення паролю було надіслано на '
              'вашу пошту', 'info')
        return redirect(url_for('user_bp_in.login'))
    return render_template('request_password_reset.html', form=form)


@user_bp.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_password(token):
    # if current_user.is_authenticated:
    #     return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('Посилання на зміну паролю більше не активне', 'warning')
        return redirect(url_for('request_password_reset'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.password = bcrypt.generate_password_hash(
            form.new_password.data).decode('utf-8')
        db.session.commit()
        try:
            db.session.commit()
            flash('Ваш пароль оновлено!', 'success')
        except:
            db.session.rollback()
            flash('Трапилась помилка. От халепа!', 'danger')

        return redirect(url_for('user_bp_in.login'))
    return render_template('reset_password.html', form=form)
