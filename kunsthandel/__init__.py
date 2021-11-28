import os

from flask import Flask, request
from flask_babel import Babel, lazy_gettext
from flask_debugtoolbar import DebugToolbarExtension
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, current_user

from kunsthandel.config import DevelopmentConfig, ProductionConfig

db = SQLAlchemy(use_native_unicode="utf8")
babel = Babel()
bcrypt = Bcrypt()
login_manager = LoginManager()
toolbar = DebugToolbarExtension()
login_manager.login_view = "users.login"
login_manager.login_message_category = "warning"
login_manager.login_message = lazy_gettext("Please log in to access this page")


def create_app(config_class=None):
    base_dir = os.path.abspath(os.path.dirname(__file__))

    app = Flask(__name__)
    if config_class is None:  # pragma: no cover
        if app.env == "development":
            config_class = DevelopmentConfig
        elif app.env == "production":
            config_class = ProductionConfig
    app.config.from_object(config_class)

    babel.init_app(app)

    db.init_app(app)

    bcrypt.init_app(app)
    login_manager.init_app(app)
    toolbar.init_app(app)

    from kunsthandel.main.routes import main
    from kunsthandel.users.routes import users
    from kunsthandel.admin.routes import admin
    from kunsthandel.items.routes import items
    from kunsthandel.generic_type.routes import generic_type
    from kunsthandel.errors.handlers import errors
    app.register_blueprint(main)
    app.register_blueprint(users)
    app.register_blueprint(admin)
    app.register_blueprint(items)
    app.register_blueprint(generic_type)
    app.register_blueprint(errors)

    with app.app_context():
        prepare_database(app, db)

    return app


def prepare_database(app, db):
    db.create_all()
    from kunsthandel.models import create_account
    from kunsthandel.models import Role
    from kunsthandel.models import User
    if User.query.count() < 1:  # Create first admin account - this is supposed to be a temporary account until
        # replaced by an actual administrator account
        root_admin = create_account(username="admin", password="admin", role=Role.Administrator)
        db.session.add(root_admin)
        db.session.commit()


@babel.localeselector
def get_locale():
    if current_user and current_user.is_authenticated:
        return current_user.locale
    if request:
        return request.accept_languages.best_match(["de", "en"])
    return "en"  # pragma: no cover
