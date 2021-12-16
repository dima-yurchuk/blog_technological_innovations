import unittest
from flask_testing import TestCase
from app import db, create_app

import re

app = create_app()
app.config.update(SQLALCHEMY_DATABASE_URI='sqlite:///testing.db',
                  SECRET_KEY='asfdsfsaaffdf', WTF_CSRF_ENABLED=False,
                  IMG_STORAGE_URL='https://res.cloudinary.com/hzulapzqj/'
                                  'image/upload/v1639663786/pictures_dev/',
                  IMG_STORAGE_FOLDER='pictures_dev',
                  NUM_PER_PAGE=10)
# from flask import url_for
from app.user.models import User
from app.blog.models import Category, Post


class BaseTestCase(TestCase):

    def create_app(self):
        return app

    def setUp(self):
        db.drop_all()
        db.create_all()
        db.session.add_all([
            User(username='tester01',
                 email='tester01@gmail.com',
                 password='qwerTy#45'),
            User(username='unit_tester_comment',
                 email='unit_tester_comment@gmail.com',
                 password='qwerTy#45'),
            Category(name='Смартфони'),
            Category(name='Ноутбуки'),
            Post(category_id=1, user_id=1, title='Назва блогу 1',
                 content='text text text text'),
            Post(category_id=2, user_id=2, title='Назва блогу 2',
                 content='text text text text'),
            Post(category_id=1, user_id=1, title='Назва блогу 3',
                 content='text text text text'),
            Post(category_id=2, user_id=2, title='Назва блогу 4',
                 content='text text text text'),
            Post(category_id=1, user_id=1, title='Назва блогу 5',
                 content='text text text text'),
            Post(category_id=1, user_id=1, title='The Best blog12',
                 content='text text text text'),
            Post(category_id=1, user_id=1, title='Супер Найкращий блог12',
                 content='text text text text'),
            Post(category_id=1, user_id=1,
                 title='Найкращий бюджетний смартфон',
                 content='text text text text'),
            Post(category_id=1, user_id=2,
                 title='Найкращий флагманський смартфон',
                 content='text text text text'),
            Post(category_id=1, user_id=1,
                 title='Найкращий смартфон',
                 content='text text text text')
        ])
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()


class TestsSearch(BaseTestCase):
    # перевірка пошуку українською
    def test_search_english(self):
        with app.test_client() as c:
            response = c.get('/search', query_string={'query': 'Best'})
            self.assert200(response)
            self.assertTrue(re.search(
                r'<h2><a class="article-title" '
                r'href="/post/[\d]+">[\w\W]*Best[\w\W]*</a></h2>',
                response.get_data(as_text=True)))

    # перевірка пошуку українською
    def test_search_ukrainian(self):
        with app.test_client() as c:
            response = c.get('/search', query_string={'query': 'Найкращий'})
            self.assert200(response)
            self.assertTrue(re.search(
                r'<h2><a class="article-title" '
                r'href="/post/[\d]+">[\w\W]*Найкращий[\w\W]*</a></h2>',
                response.get_data(as_text=True)))

    def test_search_english_with_space(self):
        with app.test_client() as c:
            response = c.get('/search', query_string={'query': 'The Best'})
            self.assert200(response)
            self.assertTrue(re.search(
                r'<h2><a class="article-title" '
                r'href="/post/[\d]+">[\w\W]*The Best[\w\W]*</a></h2>',
                response.get_data(as_text=True)))

    def test_search_ukrainian_with_space(self):
        with app.test_client() as c:
            response = c.get('/search',
                             query_string={'query': 'Супер Найкращий'})
            self.assert200(response)
            self.assertTrue(re.search(
                r'<h2><a class="article-title" '
                r'href="/post/[\d]+">[\w\W]*Супер Найкращий[\w\W]*</a></h2>',
                response.get_data(as_text=True)))

    def test_search_english_with_number(self):
        with app.test_client() as c:
            response = c.get('/search', query_string={'query': 'blog12'})
            self.assert200(response)
            self.assertTrue(re.search(
                r'<h2><a class="article-title" '
                r'href="/post/[\d]+">[\w\W]*blog12[\w\W]*</a></h2>',
                response.get_data(as_text=True)))

    def test_search_ukrainian_with_number(self):
        with app.test_client() as c:
            response = c.get('/search', query_string={'query': 'блог12'})
            self.assert200(response)
            self.assertTrue(re.search(
                r'<h2><a class="article-title" '
                r'href="/post/[\d]+">[\w\W]*блог12[\w\W]*</a></h2>',
                response.get_data(as_text=True)))

    def test_search_several(self):
        response = self.client.get('/search',
                                   query_string={'query': 'Назва блогу'},
                                   content_type='html/text')
        self.assert200(response)
        self.assertTemplateUsed('search_results.html')

        # дістаємо назви усіх знайдених публікацій
        found_posts = re.findall(
            r'<a class="article-title" href="/post/\d+?">(.+?)</a>',
            response.get_data(as_text=True))
        list_for_maching = ['Назва блогу 1', 'Назва блогу 2', 'Назва блогу 3',
                            'Назва блогу 4', 'Назва блогу 5']
        self.assertTrue(found_posts.sort() == list_for_maching.sort())

    def test_search_by_keywords(self):
        response = self.client.get('/search',
                                   query_string={'query': 'Найкращий смартфон'}
                                   , content_type='html/text')
        self.assert200(response)
        self.assertTemplateUsed('search_results.html')

        # дістаємо назви усіх знайдених за ключ.словами публікацій
        found_posts = re.findall(
            r'<a class="article-title" href="/post/\d+?">(.+?)</a>',
            response.get_data(as_text=True))
        self.assertTrue(found_posts.sort() ==
                        ['Найкращий бюджетний смартфон',
                         'Найкращий флагманський смартфон',
                         'Найкращий смартфон'].sort())


if __name__ == '__main__':
    unittest.main()
