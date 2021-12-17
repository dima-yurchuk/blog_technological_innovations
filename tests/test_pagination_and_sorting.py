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
                  NUM_PER_PAGE=2)
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
                 created_at=date_list[6]),
            Like(user_id=4, post_id=1, status=True),
            Like(user_id=2, post_id=1, status=True),
            Like(user_id=3, post_id=1, status=False),
            Like(user_id=2, post_id=2, status=True),
            Like(user_id=4, post_id=2, status=False),
            Like(user_id=1, post_id=4, status=False),
            Like(user_id=3, post_id=4, status=False),
            Like(user_id=4, post_id=4, status=False),
            Like(user_id=2, post_id=5, status=True),
            Like(user_id=3, post_id=5, status=True),
            Like(user_id=4, post_id=5, status=True)
        ]
        )
        db.session.commit()
        # posts = Post.query
        # for p in posts:
        #     print(p)

    def tearDown(self):
        db.session.remove()
        db.drop_all()


class TestsPagination(BaseTestCase):
    # print("+/-/+-/+-/+-/+-/+-/+-/+-/+-/+-/+-/+-/+-/+-/+")
    # print(sum(1 for _ in app.url_map.iter_rules()))
    # for rule in app.url_map.iter_rules():
    #     print(rule)

    def test_pagination_on_start_home_page(self):
        response = self.client.get('/', content_type='html/text')
        # print(response.get_data(as_text=True))
        self.assert200(response)
        self.assertTemplateUsed('home.html')

        # рахуємо кількість публікацій на одній сторінці
        all_posts_titles = re.findall(
            r'<a class="article-title" href="/post/\d+?">(.+?)</a>',
            response.get_data(as_text=True))
        self.assertTrue(len(all_posts_titles) == 2)

        # перевіряємо значення першої публікації на сторінці
        first_post_title = re.search(
            r'<a class="article-title" href="/post/\d+?">(.+?)</a>',
            response.get_data(as_text=True)).group(1)
        # print(first_title)
        self.assertTrue(first_post_title == 'Публікація №7 (newest)')

        # перевіряємо відображення кнопок
        list_of_pages = re.findall(
            r'<li class="page-item.+?\d+?">(\d+?)</a></li>',
            response.get_data(as_text=True)
        )
        self.assertTrue(list_of_pages == ['1', '2', '3', '4'])

        # перевіряємо активну кнопку
        active_btn = re.search(
            r'<li class="page-item active".+?\d+?">(\d+?)</a></li>',
            response.get_data(as_text=True)).group(1)
        self.assertTrue(active_btn == '1')

        # print(response.get_data(as_text=True))

    def test_pagination_another_pages(self):
        response = self.client.get('/', query_string={'page': '2'},
                                   content_type='html/text')
        self.assert200(response)
        # рахуємо кількість публікацій на одній сторінці
        all_posts_titles = re.findall(
            r'<a class="article-title" href="/post/\d+?">(.+?)</a>',
            response.get_data(as_text=True))
        self.assertTrue(len(all_posts_titles) == 2)

        # перевіряємо значення першої публікації на сторінці
        first_post_title = re.search(
            r'<a class="article-title" href="/post/\d+?">(.+?)</a>',
            response.get_data(as_text=True)).group(1)
        self.assertTrue(first_post_title == 'Публікація №5 (best)')

        # перевіряємо відображення кнопок
        list_of_pages = re.findall(
            r'<li class="page-item.+?\d+?">(\d+?)</a></li>',
            response.get_data(as_text=True)
        )
        self.assertTrue(list_of_pages == ['1', '2', '3', '4'])

        # перевіряємо активну кнопку
        active_btn = re.search(
            r'<li class="page-item active".+?\d+?">(\d+?)</a></li>',
            response.get_data(as_text=True)).group(1)
        self.assertTrue(active_btn == '2')

        # перевіряємо останню сторінку
        response = self.client.get('/', query_string={'page': '4'},
                                   content_type='html/text')
        self.assert200(response)
        # рахуємо кількість публікацій на одній сторінці
        all_posts_titles = re.findall(
            r'<a class="article-title" href="/post/\d+?">(.+?)</a>',
            response.get_data(as_text=True))
        self.assertTrue(len(all_posts_titles) == 1)

        # перевіряємо значення першої публікації на сторінці
        first_post_title = re.search(
            r'<a class="article-title" href="/post/\d+?">(.+?)</a>',
            response.get_data(as_text=True)).group(1)
        self.assertTrue(first_post_title == 'Публікація №1 (oldest)')

        # перевіряємо активну кнопку
        active_btn = re.search(
            r'<li class="page-item active".+?\d+?">(\d+?)</a></li>',
            response.get_data(as_text=True)).group(1)
        self.assertTrue(active_btn == '4')


class TestSorting(BaseTestCase):
    def test_sorting_by_default(self):
        response = self.client.get('/', content_type='html/text')
        self.assert200(response)
        self.assertTemplateUsed('home.html')

        # перша публікація на сторінці - найшовіша
        first_post_title = re.search(
            r'<a class="article-title" href="/post/\d+?">(.+?)</a>',
            response.get_data(as_text=True)).group(1)
        # print(first_title)
        self.assertTrue(first_post_title == 'Публікація №7 (newest)')

        # перевіряємо останню сторінку
        response = self.client.get('/', query_string={'page': '4'},
                                   content_type='html/text')
        self.assert200(response)
        # рахуємо кількість публікацій на на останній
        all_posts_titles = re.findall(
            r'<a class="article-title" href="/post/\d+?">(.+?)</a>',
            response.get_data(as_text=True))
        self.assertTrue(len(all_posts_titles) == 1)

        # остання публікація - найстаріша
        first_post_title = re.search(
            r'<a class="article-title" href="/post/\d+?">(.+?)</a>',
            response.get_data(as_text=True)).group(1)
        self.assertTrue(first_post_title == 'Публікація №1 (oldest)')

    def test_sorting_by_oldest(self):
        response = self.client.get('/',
                                   query_string={'sort_by': 'oldest'},
                                   content_type='html/text')
        self.assert200(response)
        self.assertTemplateUsed('home.html')

        # print(response.get_data(as_text=True))

        # перша публікація - найстаріша
        first_post_title = re.search(
            r'<a class="article-title" href="/post/\d+?">(.+?)</a>',
            response.get_data(as_text=True)).group(1)
        # print(first_title)
        self.assertTrue(first_post_title == 'Публікація №1 (oldest)')
        self.assertFalse(first_post_title == 'Публікація №7 (newest)')

        # перевіряємо останню сторінку
        response = self.client.get('/', query_string={'sort_by': 'oldest',
                                                      'page': '4'},
                                   content_type='html/text')
        self.assert200(response)
        # рахуємо кількість публікацій на останній
        all_posts_titles = re.findall(
            r'<a class="article-title" href="/post/\d+?">(.+?)</a>',
            response.get_data(as_text=True))
        self.assertTrue(len(all_posts_titles) == 1)

        # остання публікація - найновіша
        first_post_title = re.search(
            r'<a class="article-title" href="/post/\d+?">(.+?)</a>',
            response.get_data(as_text=True)).group(1)
        self.assertTrue(first_post_title == 'Публікація №7 (newest)')
        self.assertFalse(first_post_title == 'Публікація №1 (oldest)')

    def test_sorting_by_newest(self):
        response = self.client.get('/',
                                   query_string={'sort_by': 'newest'},
                                   content_type='html/text')
        self.assert200(response)
        self.assertTemplateUsed('home.html')

        # перша публікація на сторінці - найшовіша
        first_post_title = re.search(
            r'<a class="article-title" href="/post/\d+?">(.+?)</a>',
            response.get_data(as_text=True)).group(1)
        # print(first_title)
        self.assertTrue(first_post_title == 'Публікація №7 (newest)')
        self.assertFalse(first_post_title == 'Публікація №1 (oldest)')

        # перевіряємо останню сторінку
        response = self.client.get('/',
                                   query_string={'sort_by': 'newest',
                                                 'page': '4'},
                                   content_type='html/text')
        self.assert200(response)
        # рахуємо кількість публікацій на на останній
        all_posts_titles = re.findall(
            r'<a class="article-title" href="/post/\d+?">(.+?)</a>',
            response.get_data(as_text=True))
        self.assertTrue(len(all_posts_titles) == 1)

        # остання публікація - найстаріша
        first_post_title = re.search(
            r'<a class="article-title" href="/post/\d+?">(.+?)</a>',
            response.get_data(as_text=True)).group(1)
        self.assertTrue(first_post_title == 'Публікація №1 (oldest)')
        self.assertFalse(first_post_title == 'Публікація №7 (newest)')

    def test_sorting_by_best(self):
        response = self.client.get('/',
                                   query_string={'sort_by': 'best'},
                                   content_type='html/text')
        self.assert200(response)
        self.assertTemplateUsed('home.html')

        # перша публікація на сторінці - найшовіша
        first_post_title = re.search(
            r'<a class="article-title" href="/post/\d+?">(.+?)</a>',
            response.get_data(as_text=True)).group(1)
        # print(first_title)
        self.assertTrue(first_post_title == 'Публікація №5 (best)')
        self.assertFalse(first_post_title == 'Публікація №4 (worst)')

        # перевіряємо останню сторінку
        response = self.client.get('/',
                                   query_string={'sort_by': 'best',
                                                 'page': '4'},
                                   content_type='html/text')
        self.assert200(response)
        # рахуємо кількість публікацій на на останній
        all_posts_titles = re.findall(
            r'<a class="article-title" href="/post/\d+?">(.+?)</a>',
            response.get_data(as_text=True))
        self.assertTrue(len(all_posts_titles) == 1)

        # остання публікація - найстаріша
        first_post_title = re.search(
            r'<a class="article-title" href="/post/\d+?">(.+?)</a>',
            response.get_data(as_text=True)).group(1)
        self.assertTrue(first_post_title == 'Публікація №4 (worst)')
        self.assertFalse(first_post_title == 'Публікація №5 (best)')

    def test_sorting_by_best_order(self):
        response = self.client.get('/',
                                   query_string={'sort_by': 'best'},
                                   content_type='html/text')
        self.assert200(response)
        self.assertTemplateUsed('home.html')

        # перша публікація на сторінці - найшовіша
        all_posts_titles = re.findall(
            r'<a class="article-title" href="/post/\d+?">(.+?)</a>',
            response.get_data(as_text=True))
        # Публікація №5 (3:likes 0:dis) Публікація №1 (2:likes 1:dis)
        self.assertTrue(all_posts_titles == ['Публікація №5 (best)',
                                             'Публікація №1 (oldest)'])

        response = self.client.get('/',
                                   query_string={'sort_by': 'best',
                                                 'page': '2'},
                                   content_type='html/text')
        self.assert200(response)
        all_posts_titles = re.findall(
            r'<a class="article-title" href="/post/\d+?">(.+?)</a>',
            response.get_data(as_text=True))
        # Публікація №2 (1:likes 1:dis)
        # Публікація №7 (0:likes 0:dis), але вища за іних з нулями лайків і
        # дизлайків - через новішу дату
        # print(all_posts_titles)
        self.assertTrue(all_posts_titles == ['Публікація №2',
                                             'Публікація №7 (newest)'])


if __name__ == '__main__':
    unittest.main()
