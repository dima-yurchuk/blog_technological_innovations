from flask import redirect, url_for, flash
from flask_admin import BaseView, expose, AdminIndexView
from flask_login import current_user
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.fileadmin import FileAdmin
from .forms import check_letters, check_digits, check_symbols, check_spaces
from wtforms.validators import Length, DataRequired, Regexp, Email

from ..blog.forms import check_text_length
from app.blog.models import Post, Comment, Like
from app import db


class MyHomeView(AdminIndexView):
    @expose('/')
    def index(self):
        if not (current_user.is_authenticated and current_user.admin):
            flash('Немає доступу до цієї сторінки',
                  'danger')
            return redirect(url_for('user_bp_in.login'))
        return self.render('admin/admin_home.html')


class UserModelView(ModelView):
    column_searchable_list = ('username',)
    column_sortable_list = ('username',)
    column_list = ('username', 'email', 'picture', 'admin',)
    column_labels = {
        'username': "Ім'я користувача",
        'picture': 'Фото',
        'admin': 'Є адміном',
    }
    form_edit_rules = (
        'username', 'email', 'picture', 'admin',
    )
    form_create_rules = (
        'username', 'email', 'password', 'admin'
    )
    form_args = dict(
        username=dict(validators=[Length(min=3, max=30,
                                         message='Поле повинно бути довжиною '
                                                 'від 3 до 30 симолів!'),
                                  DataRequired(message='Заповніть це поле!'),
                                  Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                         "Ім'я повинно містити тільки "
                                         "англійські літери, "
                                         "цифри, крапку або нижнє "
                                         "підкреслення!")
                                  ]),
        email=dict(validators=[DataRequired(message='Заповніть це поле!'),
                               Email(message='Некоректна email адреса!')]),
        password=dict(label='Пароль',
                      validators=[Length(min=8, max=30,
                                         message='Поле повинно бути довжиною '
                                                 'від 3 до 30 симолів!'),
                                  DataRequired(message='Заповніть це поле!'),
                                  check_letters, check_digits, check_symbols,
                                  check_spaces]),
    )

    def is_accessible(self):
        return current_user.is_authenticated and current_user.admin

    def inaccessible_callback(self, name, *kwargs):
        flash('Немає доступу до цієї сторінки',
              'danger')
        return redirect(url_for('home'))

    def delete_model(self, model):
        try:
            posts = Post.query.filter_by(user_id=model.id)
            if posts.first():
                for post in posts:
                    comments = Comment.query.filter_by(post_id=post.id)
                    likes = Like.query.filter_by(post_id=post.id)
                    if comments.first() or likes.first():
                        for comment in comments:
                            db.session.delete(comment)
                        for like in likes:
                            db.session.delete(like)
                    db.session.delete(post)
                self.session.delete(model)
                self.session.commit()
                return True
            else:
                self.session.delete(model)
                self.session.commit()
                return True
        except:
            self.session.rollback()
            return False


class CategoryModelView(ModelView):
    can_create = False
    can_edit = False
    can_delete = False
    column_searchable_list = ('name',)
    column_sortable_list = ('name',)
    column_list = ('name',)
    column_labels = {
        'name': "Категорія"
    }
    form_edit_rules = (
        'name',
    )
    form_create_rules = (
        'name',
    )

    def is_accessible(self):
        return current_user.is_authenticated and current_user.admin

    def inaccessible_callback(self, name, *kwargs):
        flash('Немає доступу до цієї сторінки',
              'danger')
        return redirect(url_for('home'))

    def delete_model(self, model):
        try:
            posts = Post.query.filter_by(category_id=model.id)
            if posts.first():
                flash('You cannot delete a category because there are posts'
                      ' with this category', 'danger')
            else:
                self.session.delete(model)
                self.session.commit()
                return True
        except:
            self.session.rollback()
            return False


class PostModelView(ModelView):
    def _content_formatter(view, context, model, name):
        # Format your string here e.g show first 20 characters
        # can return any valid HTML e.g. a link to another view to
        # show the detail or a popup window
        return model.content[:50]

    can_create = False
    column_formatters = {
        'content': _content_formatter,
    }
    column_searchable_list = ('title',)
    column_sortable_list = ('title', 'created_at', 'user_br.username',
                            'category_br.name')
    column_list = ('category_br.name', 'user_br.username', 'title', 'content',
                   'created_at', 'total_likes', 'total_dislikes',
                   'total_comments')
    column_labels = {
        'category_br.name': 'Категорія',
        'user_br.username': 'Користувач',
        'title': 'Заголовок',
        'content': 'Опис',
        'created_at': 'Дата створення',
        'total_likes': 'Кількість лайків',
        'total_dislikes': 'Кількість дизлайків',
        'total_comments': 'Кількість коментарів'
    }
    form_edit_rules = (
        'category_br', 'user_br', 'title', 'content',
    )
    form_create_rules = (
        'category_br', 'user_br', 'title', 'content',
    )
    form_args = dict(
        title=dict(label='Заголовок',
                   validators=[Length(min=5, max=100, message='Заголовок '
                                                              'повинен'
                                                              ' бути довжиною '
                                                              'від 5 до 100'
                                                              ' симолів!'),
                               DataRequired(message='Публікація повинна мати'
                                                    ' заголовок')]),
        content=dict(label='Опис', validators=[check_text_length]),
        category_br=dict(label='Категорія', validators=[DataRequired(
            message='Публікація повинна мати категорію')]),
        user_br=dict(label='Користувач', validators=[DataRequired(
            message='Публікація повинна мати користувача')]),
    )
    create_template = 'admin/post_content.html'
    edit_template = 'admin/post_content.html'

    def is_accessible(self):
        return current_user.is_authenticated and current_user.admin

    def inaccessible_callback(self, name, *kwargs):
        flash('Немає доступу до цієї сторінки',
              'danger')
        return redirect(url_for('home'))

    def delete_model(self, model):
        try:
            comments = Comment.query.filter_by(post_id=model.id)
            likes = Like.query.filter_by(post_id=model.id)
            if comments.first() or likes.first():
                for comment in comments:
                    db.session.delete(comment)
                for like in likes:
                    db.session.delete(like)
                self.session.delete(model)
                self.session.commit()
                return True
            else:
                self.session.delete(model)
                self.session.commit()
                return True
        except:
            self.session.rollback()
            return False


class LikeModelView(ModelView):
    can_create = False
    can_edit = False
    column_list = ('user_br.username', 'post_br.title', 'status')
    column_sortable_list = ('user_br.username', 'post_br.title')
    column_labels = {
        'user_br.username': 'Користувач',
        'post_br.title': 'Пост',
        'status': 'Статус(лайк/дизлайк)',
    }
    form_args = dict(
        post_br=dict(label='Пост', validators=[DataRequired(
            message="Це поле є обов'язковим")]),
        user_br=dict(label='Користувач', validators=[DataRequired(
            message="Це поле є обов'язковим")]),
        status=dict(label='Статус(лайк/дизлайк)'),
    )

    def is_accessible(self):
        return current_user.is_authenticated and current_user.admin

    def inaccessible_callback(self, name, *kwargs):
        flash('Немає доступу до цієї сторінки',
              'danger')
        return redirect(url_for('home'))


class CommentModelView(ModelView):
    can_create = False
    column_list = ('user_br.username', 'post_br.title', 'text', 'created_at')
    column_sortable_list = ('user_br.username', 'post_br.title', 'created_at',)
    column_labels = {
        'user_br.username': 'Користувач',
        'post_br.title': 'Пост',
        'text': 'Текст коментаря',
        'created_at': 'Дата створення',
    }
    form_args = dict(
        post_br=dict(label='Пост', validators=[DataRequired(
            message="Це поле є обов'язковим")]),
        user_br=dict(label='Користувач', validators=[DataRequired(
            message="Це поле є обов'язковим")]),
        text=dict(label='Текст коментаря',
                  validators=[Length(min=3, max=500,
                                     message='Коментар повинен бути довжиною '
                                             'від 5 до 100 симолів!'),
                              DataRequired(message='Коментар не може бути'
                                                   ' пустим!')]),
        created_at=dict(label='Дата створення'),
    )

    def is_accessible(self):
        return current_user.is_authenticated and current_user.admin

    def inaccessible_callback(self, name, *kwargs):
        flash('Немає доступу до цієї сторінки',
              'danger')
        return redirect(url_for('home'))


class CustomFileAdmin(FileAdmin):
    column_list = ('name',)
    column_labels = {
        'name': "Назва"
    }

    def is_accessible(self):
        return current_user.is_authenticated and current_user.admin

    def inaccessible_callback(self, name, *kwargs):
        flash('Немає доступу до цієї сторінки',
              'danger')
        return redirect(url_for('home'))
