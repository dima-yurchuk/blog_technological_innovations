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
from flask_login import current_user


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
                 content='text text text text')
        ])
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()


class TestsCRUD(BaseTestCase):
    # тест створення поста для неавторизованого користувача
    def test_create_post(self):
        response = self.client.get('/post/create')
        self.assert401(response)

        response = self.client.post('/post/create',
                                    data={'category': 2,
                                          'title': 'New post',
                                          'content': 'restsdfffffffffgggdfg'
                                                     'hgfgh '},
                                    follow_redirects=True)
        self.assertNotEqual(response.status_code, 200)

    # тест перегляду постів для неавторизованого користувача
    def test_view_post(self):
        for i in range(1, 6):
            response = self.client.get(f'post/{i}')
            self.assert200(response)

            user_id = db.session.query(Post).filter(
                Post.id == i)[0].user_id
            username = db.session.query(User).filter(
                User.id == user_id)[0].username

            self.assertTrue(
                f'<h3 class="text-center mb-0">Назва блогу {i}</h3>'
                in response.get_data(as_text=True))

            self.assertTrue('text text text text'
                            in response.get_data(as_text=True))

            self.assertTrue(username in response.get_data(as_text=True))

    # тест оновлення постів для неавторизованого користувача
    def test_update_post(self):
        for i in range(1, 6):
            response = self.client.get(f'post/{i}/update')
            self.assert403(response)

            response = self.client.post(f'post/{i}/update',
                                        data={'category': 1,
                                              'title': 'Updated post',
                                              'content': 'text text '
                                                         'text text'},
                                        follow_redirects=True)

            self.assertNotEqual(response.status_code, 200)

    # тест видалення постів для неавторизованого користувача
    def test_delete_post(self):
        for i in range(1, 6):
            response = self.client.get(f'post/{i}/delete')
            self.assert403(response)

    # тест успішного створення поста для авторизованого користувача
    def test_auth_create_post_succesfull(self):
        with self.client:
            response = self.client.post('/auth/login',
                                        data={'email': 'tester01@gmail.com',
                                              'password': 'qwerTy#45'},
                                        follow_redirects=True)

            self.assert200(response)

            response = self.client.get('/post/create')
            self.assert200(response)

            response = self.client.post('/post/create',
                                        data={'category': 1,
                                              'title': 'Post_tester22',
                                              'content': 'gchkfyukhklvmccgf'
                                                         'sdfbxcvbfhghf'},
                                        follow_redirects=True)
            self.assert200(response)

            self.assertMessageFlashed('Публікація успішно створена',
                                      category='success')
            self.assertTrue('<h3 class="text-center mb-0">Post_tester22</h3>'
                            in response.get_data(as_text=True)
                            )

    # тест неуспішного створення поста для авторизованого користувача
    def test_auth_create_post_unsuccesfull(self):
        with self.client:
            response = self.client.post('/auth/login',
                                        data={'email': 'tester01@gmail.com',
                                              'password': 'qwerTy#45'},
                                        follow_redirects=True)
            self.assert200(response)

            response = self.client.get('/post/create')
            self.assert200(response)

            response = self.client.post('/post/create',
                                        data={'category': 2,
                                              'title': 'Po',
                                              'content': 'папаапsdfh'},
                                        follow_redirects=True)
            self.assertNotEqual(response, 200)

            self.assertTrue(
                'Заголовок повинен бути довжиною від 5 до 100 симолів!'
                in response.get_data(as_text=True))

            self.assertTrue(
                'Текст повинен бути довжиною від 15 символів'
                in response.get_data(as_text=True))

    # тест перегляду постів для авторизованого користувача
    def test_auth_view_post(self):
        with self.client:
            response = self.client.post('/auth/login',
                                        data={'email': 'tester01@gmail.com',
                                              'password': 'qwerTy#45'},
                                        follow_redirects=True)

            for i in range(1, 6):
                response = self.client.get(f'post/{i}')
                self.assert200(response)

                user_id = db.session.query(Post).filter(
                    Post.id == i)[0].user_id
                username = db.session.query(User).filter(
                    User.id == user_id)[0].username

                self.assertTrue(
                    f'<h3 class="text-center mb-0">Назва блогу {i}</h3>'
                    in response.get_data(as_text=True))

                self.assertTrue('text text text text'
                                in response.get_data(as_text=True))

                self.assertTrue(username in response.get_data(as_text=True))

    # тест успішного оновлення поста для авторизованого користувача
    def test_auth_update_post_succesfull(self):
        with self.client:
            response = self.client.post('/auth/login',
                                        data={'email': 'tester01@gmail.com',
                                              'password': 'qwerTy#45'},
                                        follow_redirects=True)

            id_user = current_user.id

            for i in range(1, 6):
                post = db.session.query(Post).filter(Post.id == i)
                id_post_user = post[0].user_id

                response = self.client.get(f'post/{i}/update')

                if id_post_user == id_user:
                    self.assert200(response)
                else:
                    self.assertNotEqual(response.status_code, 200)

                response = self.client.post(f'post/{i}/update',
                                            data={'category': 1,
                                                  'title': f'Updated post {i}',
                                                  'content': 'text text text '
                                                             'text'},
                                            follow_redirects=True)

                if id_post_user == id_user:
                    self.assert200(response)
                else:
                    self.assertNotEqual(response.status_code, 200)

    # тест неуспішного оновлення поста для авторизованого користувача
    def test_auth_update_post_unsuccesfull(self):
        with self.client:
            response = self.client.post('/auth/login',
                                        data={'email': 'tester01@gmail.com',
                                              'password': 'qwerTy#45'},
                                        follow_redirects=True)

            id_user = current_user.id

            for i in range(1, 6):
                post = db.session.query(Post).filter(Post.id == i)
                id_post_user = post[0].user_id

                response = self.client.get(f'post/{i}/update')

                if id_post_user == id_user:
                    self.assert200(response)
                else:
                    self.assert403(response)
                    continue

                response = self.client.post(f'post/{i}/update',
                                            data={'category': 1,
                                                  'title': f'Upda',
                                                  'content': 'Text'},
                                            follow_redirects=True)

                self.assertNotEqual(response, 200)

                self.assertTrue(
                    'Заголовок повинен бути довжиною від 5 до 100 симолів!'
                    in response.get_data(as_text=True))

                self.assertTrue(
                    'Текст повинен бути довжиною від 15 символів'
                    in response.get_data(as_text=True))

    # тест видалення постів для авторизованого користувача
    def test_auth_delete(self):
        with self.client:
            response = self.client.post(
                '/auth/login',
                data={'email': 'tester01@gmail.com',
                      'password': 'qwerTy#45'},
                follow_redirects=True)

            current_d_user = current_user.id

            for i in range(5, 0, -1):
                post = db.session.query(Post).filter(Post.id == i)
                id_post_user = post[0].user_id

                response = self.client.get(
                    f'/post/{i}/delete', follow_redirects=True)

                if current_d_user == id_post_user:
                    self.assert200(response)
                    # перевіряємо, чи можна зайти на видалену сторінку
                    response = self.client.get(f'post/{i}')
                    self.assert404(response)
                else:
                    self.assert403(response)


if __name__ == '__main__':
    unittest.main()
