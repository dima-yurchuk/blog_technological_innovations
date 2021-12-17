import unittest
from flask_testing import TestCase
from flask import url_for
from app import db, create_app

import re
import datetime

app = create_app()
app.config.update(SQLALCHEMY_DATABASE_URI='sqlite:///testing.db',
                  SECRET_KEY='asfdsfsaaffdf', WTF_CSRF_ENABLED=False,
                  IMG_STORAGE_URL='https://res.cloudinary.com/hzulapzqj/'
                                  'image/upload/v1639663786/pictures_dev/',
                  NUM_PER_PAGE=10)
from app.views import home

app.add_url_rule('/', 'home', home)
from app.user.models import User
from app.blog.models import Category, Post, Like


class BaseTestCase(TestCase):

    def create_app(self):
        return app

    def setUp(self):
        db.drop_all()
        db.create_all()
        # потім забрати на початок
        base = datetime.datetime.now()
        date_list = [base + datetime.timedelta(days=x) for x in range(7)]
        db.session.add_all([
            User(username='tester01',
                 email='tester01@gmail.com',
                 password='qwerTy#45'),
            User(username='unit_tester_comment',
                 email='unit_tester_comment@gmail.com',
                 password='qwerTy#45'),
            User(username='IceNice',
                 email='icenice@gmail.com',
                 password='niceTy#55'),
            User(username='MrElectron',
                 email='mrelectron@gmail.com',
                 password='niceTy#55'),
            Category(name='Смартфони'),
            Category(name='Ноутбуки'),
            Post(category_id=1, user_id=1, title='Публікація №1 (oldest)',
                 content='text text text text',
                 created_at=date_list[0]),
            Post(category_id=2, user_id=1, title='Публікація №2',
                 content='text text text text',
                 created_at=date_list[1]),
            Post(category_id=1, user_id=1, title='Публікація №3',
                 content='text text text text',
                 created_at=date_list[2]),
            Post(category_id=2, user_id=2, title='Публікація №4 (worst)',
                 content='text text text text',
                 created_at=date_list[3]),
            Post(category_id=1, user_id=1, title='Публікація №5 (best)',
                 content='text text text text',
                 created_at=date_list[4]),
            Post(category_id=1, user_id=1, title='Публікація №6',
                 content='text text text text',
                 created_at=date_list[5]),
            Post(category_id=1, user_id=1, title='Публікація №7 (newest)',
                 content='text text text text',
                 created_at=date_list[6])
        ]
        )
        db.session.commit()
        # posts = Post.query
        # for p in posts:
        #     print(p)

    def tearDown(self):
        db.session.remove()
        db.drop_all()


class TestsPostsViewByCategories(BaseTestCase):

    def test_view_posts_by_category(self):
        response = self.client.get('/category/1', content_type='html/text')
        self.assert200(response)
        self.assertTemplateUsed('posts_by_category.html')

        self.assertTrue(
            f'<b class="text-uppercase">'
            f'{Category.query.get(1).name}'
            in response.get_data(as_text=True)
        )

        list_posts_from_page = re.findall(
            r'<a class="article-title" href="/post/\d+?">(.+?)</a>',
            response.get_data(as_text=True))
        posts_from_db = Post.query.filter(Post.category_id == 1)
        # print(list_posts_from_page)

        # перевіряємо чи спіпадає загальна кількість публікацій
        # на сторінці категорії із фактичною, в БД
        self.assertTrue(len(list_posts_from_page) == posts_from_db.count())

        list_of_posts_from_db = [post.title for post in posts_from_db]
        # print(list_of_posts_from_db)
        # перевіряємо чи співпадають публікації на сторінці і в БД
        self.assertTrue(list_posts_from_page.sort() == list_of_posts_from_db.
                        sort())


class TestsPostsViewByUsers(BaseTestCase):
    def test_view_posts_by_user(self):
        response = self.client.get('/user_posts/1', content_type='html/text')
        self.assert200(response)
        self.assertTemplateUsed('user_posts.html')

        self.assertTrue(
            f'<a class="author-name separator" href="/user_posts/1">'
            f'{User.query.get(1).username}</a>'
            in response.get_data(as_text=True)
        )
        self.assertFalse(
            f'<a class="author-name separator" href="/user_posts/1">'
            f'Taras_Tarasovych</a>'
            in response.get_data(as_text=True)
        )

        list_posts_from_page = re.findall(
            r'<a class="article-title" href="/post/\d+?">(.+?)</a>',
            response.get_data(as_text=True))
        posts_from_db = Post.query.filter(Post.user_id == 1)
        # print(list_posts_from_page)

        # перевіряємо чи спіпадає загальна кількість публікацій
        # на сторінці категорії із фактичною, в БД
        self.assertTrue(len(list_posts_from_page) == posts_from_db.count())

        list_of_posts_from_db = [post.title for post in posts_from_db]
        # print(list_of_posts_from_db)
        # перевіряємо чи співпадають публікації на сторінці і в БД
        self.assertTrue(list_posts_from_page.sort() == list_of_posts_from_db.
                        sort())


if __name__ == '__main__':
    unittest.main()
