from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_msearch import Search
import os
import cloudinary


# app = Flask(__name__)
# app.config.from_object('config')
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
mail = Mail()
search = Search()


def create_app(config_filename=None):
    app = Flask(__name__, instance_relative_config=True)
    with app.app_context():
        app.config.from_object('config')
        if os.environ.get('FLASK_ENV') == 'development':  # for local work
            app.config.update(
                SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL_DEV'),
                IMG_STORAGE_URL=os.environ.get('IMG_STORAGE_URL_DEV'),
                IMG_STORAGE_FOLDER=os.environ.get('IMG_STORAGE_FOLDER_DEV')
            )
        else:  # for heroku work
            app.config.update(
                SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL_PROD'),
                IMG_STORAGE_URL=os.environ.get('IMG_STORAGE_URL_PROD'),
                IMG_STORAGE_FOLDER=os.environ.get('IMG_STORAGE_FOLDER_PROD')
            )
        db.init_app(app)
        bcrypt.init_app(app)
        login_manager.init_app(app)
        mail.init_app(app)
        search.init_app(app)
        cloudinary.config(
            cloud_name="hzulapzqj",
            api_key="738641162426987",
            api_secret="SJBAvXWpcDJJhsFzVz_sOMN07fw"
        )
        from .blog import blog_bp  # pylint: disable=import-error
        from .user import user_bp  # pylint: disable=import-error
        app.register_blueprint(blog_bp, url_prefix='')
        app.register_blueprint(user_bp, url_prefix='/auth')
        from .user import create_module as admin_create_module
        admin_create_module(app)
        from app import views  # noqa # linting: disable=unused-import
        from app import forms  # noqa # linting: disable=unused-import
    return app
