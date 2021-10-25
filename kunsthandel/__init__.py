import os

from flask import Flask, request
from flask_babel import Babel, gettext
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, current_user
import babel

from kunsthandel.config import DebugConfig, ProductionConfig

db = SQLAlchemy(use_native_unicode="utf8")
babel = Babel()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'

def create_app(config_class=DebugConfig):
    base_dir = os.path.abspath(os.path.dirname(__file__))


    app = Flask(__name__)
    app.config.from_object(config_class)

    app.config["BABEL_TRANSLATION_DIRECTORIES"] = "../translations"
    babel.init_app(app)

    db.init_app(app)


    bcrypt.init_app(app)
    login_manager.init_app(app)

    from kunsthandel.main.routes import main
    from kunsthandel.users.routes import users
    from kunsthandel.admin.routes import admin
    from kunsthandel.items.routes import items
    from kunsthandel.generic_type.routes import generic_type
    app.register_blueprint(main)
    app.register_blueprint(users)
    app.register_blueprint(admin)
    app.register_blueprint(items)
    app.register_blueprint(generic_type)

    with app.app_context():
        prepare_database(app, db)
    return app


def prepare_database(app, db):
    print(gettext("Preparing database"))
    db.create_all()
    from kunsthandel.models import create_account
    from kunsthandel.models import Role
    from kunsthandel.models import User
    if len(User.query.all()) < 1: # Create first admin account - this is supposed to be a temporary account until replaced by an actualy administrator account
        root_admin = create_account(username="admin", password="admin", role=Role.Administrator)
        db.session.add(root_admin)
        db.session.commit()
        print(gettext("Admin account created"))


@babel.localeselector
def get_locale():
    if current_user:
        return current_user.locale
    return "en"


