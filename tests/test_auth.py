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
                 password='qwerTy#45')
        ])
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()


# class TestHomePage(BaseTestCase):
#     def test_home_page(self):
#         response = self.client.get('/', content_type='html/text')
#         self.assert200(response)
#         self.assertTemplateUsed('home.html')
#         self.assertIn(b'TechBlog', response.data)
#         self.assertTrue('Категорії' in response.get_data(as_text=True))


class TestLoginRegistration(BaseTestCase):
    # перевірка неавторизованого користувача
    def test_access_for_unauth_user(self):
        response = self.client.get('/', content_type='html/text')
        self.assert200(response)
        self.assertTrue(
            'Увійти'
            in response.get_data(as_text=True)
        )
        self.assertFalse(
            'Мій профіль'
            in response.get_data(as_text=True)
        )
        # print(response.get_data(as_text=True))
        self.assert401(self.client.get('/auth/account'))
        self.assert401(self.client.get('/post/create'))

    # перевірка успішної реєстрації користувача
    def test_user_successful_registration(self):
        with self.client:
            response = self.client.get('/auth/register')
            self.assert200(response)
            self.assertTrue('<legend class="border-bottom mb-4">'
                            'Реєстрація</legend>'
                            in response.get_data(as_text=True))
            response = self.client.post('/auth/register',
                                        data={'username': 'unit_tester1',
                                              'email': 'team3member@gmail.com',
                                              'password': '12345qaZ!',
                                              'confirm_password': '12345qaZ!'},
                                        follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertMessageFlashed('Користувач unit_tester1 успішно '
                                      'зареєстрований!', category='success')
            self.assert401(self.client.get('auth/account'))

    # перевірка сценарію неуспішної реєстрації користувача
    def test_user_unsuccessful_registration(self):
        with self.client:
            response = self.client.get('/auth/register')
            self.assert200(response)
            self.assertTrue('<legend class="border-bottom '
                            'mb-4">Реєстрація</legend>' in
                            response.get_data(as_text=True))
            # передаємо невірні значення полів
            response = self.client.post('/auth/register',
                                        data={'username': 'tester01',
                                              'email': 'team3membergmail.com',
                                              'password': 'qwert',
                                              'confirm_password': 'qwer'},
                                        follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            # та опісля перевіряємо роботу валідаторів
            self.assertTrue('Користувач з таким іменем уже зареєстрований!'
                            in response.get_data(as_text=True))
            self.assertTrue('Некоректна email адреса!'
                            in response.get_data(as_text=True))
            self.assertTrue('Пароль повинен бути довжиною від 8 до 30 симолів!'
                            in response.get_data(as_text=True))
            self.assertTrue('Пароль повинен містити великі та малі літери'
                            in response.get_data(as_text=True))
            self.assertTrue('Пароль повинен містити цифру'
                            in response.get_data(as_text=True))
            self.assertTrue(
                'Пароль повинен містити символ(не літеру і не цифру)'
                in response.get_data(as_text=True)
            )
            self.assertTrue('Паролі не збігаються!'
                            in response.get_data(as_text=True))
            self.assert401(self.client.get('auth/account'))

    # перевірка успшної авторизації користувача
    def test_user_successful_login(self):
        with self.client:
            response = self.client.get('/auth/login')
            # response = self.client.get(url_for('user_bp_in.login'))
            self.assert200(response)
            self.assertTrue(
                '<legend class="border-bottom mb-4">Вхід</legend>' in
                response.get_data(as_text=True))
            response = self.client.post('/auth/login',
                                        data={'email': 'tester01'
                                                       '@gmail.com',
                                              'password': 'qwerTy#45'},
                                        follow_redirects=True)
            self.assert200(response)
            # redirect_url = url_for('/auth/login', next='/auth/account')
            # self.assertRedirects(response, redirect_url)
            self.assertMessageFlashed('Користувач успішно увійшов у свій '
                                      'аккаунт!', category='success')
            self.assertTrue(
                'Інформація про мене' in response.get_data(as_text=True)
            )
            self.assertTrue(
                '<em class="card-title text-muted">'
                'tester01@gmail.com</em>'
                in response.get_data(as_text=True)
            )
            # користувач тепер має доступ до сторінки аккаунту
            self.assert200(self.client.get('auth/account'))

    # перевірка сценарію неуспішної авторизації
    def test_user_unsuccessful_login(self):
        with self.client:
            response = self.client.get('/auth/login')
            # response = self.client.get(url_for('user_bp_in.login'))
            self.assert200(response)
            self.assertTrue(
                '<legend class="border-bottom mb-4">Вхід</legend>' in
                response.get_data(as_text=True))
            # якщо користувач вводить емейл, який не зареєстроваинй на сайті
            response = self.client.post('/auth/login',
                                        data={'email': 'team33memb@gmail.com',
                                              'password': '12345qaZ!'},
                                        follow_redirects=True)
            self.assert200(response)
            self.assertMessageFlashed('Користувач із вказаним емейлом не '
                                      'зареєстрований на сайті.',
                                      category='danger')
            self.assertFalse(
                '<legend class="border-bottom mb-4">Інформація '
                'про мене</legend>' in response.get_data(as_text=True))
            self.assertFalse(
                '<em class="card-title text-muted">team3member@gmail.com</em>'
                in response.get_data(as_text=True))
            self.assert401(self.client.get('auth/account'))

            # якщо користувач вводить просто некоректний емейл
            response = self.client.post('/auth/login',
                                        data={'email': 'team3membergmail.com',
                                              'password': '12345q!'},
                                        follow_redirects=True)
            self.assert200(response)
            self.assertTrue('Некоректна email адреса!'
                            in response.get_data(as_text=True))
            self.assert401(self.client.get('auth/account'))

            # якщо користувач вводить невірний пароль
            response = self.client.post('/auth/login',
                                        data={'email': 'tester01'
                                                       '@gmail.com',
                                              'password': 'qwerty345'},
                                        follow_redirects=True)
            self.assert200(response)
            self.assertMessageFlashed('Введено невірний пароль.',
                                      category='danger')
            self.assert401(self.client.get('auth/account'))


if __name__ == '__main__':
    unittest.main()
