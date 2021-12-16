import unittest
from flask_testing import TestCase
from app import db, create_app

app = create_app()
app.config.update(SQLALCHEMY_DATABASE_URI='sqlite:///testing.db',
                  SECRET_KEY='asfdsfsaaffdf', WTF_CSRF_ENABLED=False,
                  IMG_STORAGE_URL='https://res.cloudinary.com/hzulapzqj/'
                                  'image/upload/v1639663786/pictures_dev/',
                  IMG_STORAGE_FOLDER='pictures_dev')
from app.user.models import User
from app.blog.models import Category, Post, Comment


class BaseTestCase(TestCase):

    def create_app(self):
        return app

    def setUp(self):
        db.drop_all()
        db.create_all()
        db.session.add_all([
            Category(name='Смартфони'),
            Category(name='Ноутбуки'),
            User(username='tester01',
                 email='tester01@gmail.com',
                 password='qwerTy#45'),
            User(username='unit_tester_comment',
                 email='unit_tester_comment@gmail.com',
                 password='qwerTy#45'),
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
                 content='text text text text')])
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()


class TestsComments(BaseTestCase):
    # перевірка для нeавторизованого користувача
    def test_access_to_comment_for_unauth_user(self):
        comment1 = Comment(user_id=1, post_id=1, text='Test comment')
        db.session.add(comment1)
        db.session.commit()
        response = self.client.get('/post/1',
                                   content_type='html/text')
        self.assert200(response)
        self.assertFalse(
            'Коментувати'
            in response.get_data(as_text=True)
        )
        self.assertFalse(
            'Надіслати'
            in response.get_data(as_text=True)
        )
        self.assertTrue(
            'Авторизуйтесь, щоб мати можливість залишати коментарі.'
            in response.get_data(as_text=True)
        )
        # якщо користувач НЕ авторизований, він НЕ може видалити коментарі
        response = self.client.post('/comment/1/delete',
                                    follow_redirects=True)
        self.assert403(response)
        self.assertTrue(
            'Ви не маєте прав на видалення даного коментаря'
            in response.get_data(as_text=True)
        )
        # якщо користувач НЕ авторизований, він НЕ може додавати коментарі
        response = self.client.post('/post/1',
                                    data={'comment': 'Great comment!'},
                                    follow_redirects=True)
        self.assertTrue(
            'Авторизуйтесь, щоб мати можливість залишати коментарі.'
            in response.get_data(as_text=True)
        )

    # перевірка для авторизованого користувача
    def test_access_to_comment_for_auth_user(self):
        response = self.client.post('/auth/login',
                                    data={
                                        'email': 'tester01@gmail.com',
                                        'password': 'qwerTy#45'},
                                    follow_redirects=True)
        self.assert200(response)
        self.assertMessageFlashed('Користувач успішно увійшов у свій '
                                  'аккаунт!', category='success')
        # якщо користувач авторизований, він може додавати коментарі
        response = self.client.post('/post/1',
                                    data={'comment': 'Great!'},
                                    follow_redirects=True)
        self.assertTrue(
            'Коментарі'
            in response.get_data(as_text=True)
        )
        self.assertTrue(
            'Надіслати'
            in response.get_data(as_text=True)
        )
        self.assertFalse(
            'Авторизуйтесь, для того, щоб мати можливість писати коментарі'
            in response.get_data(as_text=True)
        )
        self.assertTrue(
            'Great!'
            in response.get_data(as_text=True)
        )
        # якщо користувач авторизований, він може видалити коментарі
        self.assertTrue(
            'title="Видалити"'
            in response.get_data(as_text=True)
        )
        response = self.client.post('/comment/1/delete',
                                    follow_redirects=True)
        self.assert200(response)
        self.assertFalse(
            'Great!'
            in response.get_data(as_text=True)
        )


class TestsLikes(BaseTestCase):
    # перевірка для нeавторизованого користувача
    def test_access_to_like_for_unauth_user(self):
        response = self.client.get('/post/1',
                                   content_type='html/text')
        # print(response.get_data(as_text=True))
        self.assert200(response)

        response = self.client.get('/post/1/like',
                                   content_type='html/text')
        self.assert401(response)
        self.assertTrue(
            'The server could not verify that you are authorized to access '
            'the URL requested'
            in response.get_data(as_text=True)
        )

    # перевірка для нeавторизованого користувача
    def test_access_to_like_for_auth_user(self):
        response = self.client.post('/auth/login',
                                    data={'email': 'tester01@gmail.com',
                                          'password': 'qwerTy#45'},
                                    follow_redirects=True)
        self.assert200(response)
        self.assertMessageFlashed('Користувач успішно увійшов у свій '
                                  'аккаунт!', category='success')
        response = self.client.get('/post/1',
                                   content_type='html/text')
        self.assert200(response)
        # перевірка того, що користувач НЕ може оцінювати власні пости
        response = self.client.get('/post/1/like',
                                   content_type='html/text')
        self.assert403(response)
        self.assertTrue(
            'Ви не можете оцінювати власні публікації'
            in response.get_data(as_text=True)
        )
        # перевірка того, що користувач може оцінювати чужі пости
        response = self.client.get('/post/2/like',
                                   content_type='html/text')
        self.assertTrue(
            'You should be redirected automatically to target URL:'
            in response.get_data(as_text=True)
        )
        response = self.client.get('/post/2',
                                   content_type='html/text')
        # print(response.get_data(as_text=True))
        self.assert200(response)
        self.assertTrue(
            'class="bi" data-toggle="tooltip">1</a>'
            in response.get_data(as_text=True)
        )
