from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

from kunsthandel.config import DebugConfig, ProductionConfig

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'


def create_app(config_class=DebugConfig):
    app = Flask(__name__)
    app.config.from_object(DebugConfig)

    db.init_app(app)

    bcrypt.init_app(app)
    login_manager.init_app(app)

    from kunsthandel.main.routes import main
    from kunsthandel.users.routes import users
    from kunsthandel.admin.routes import admin
    from kunsthandel.items.routes import items
    app.register_blueprint(main)
    app.register_blueprint(users)
    app.register_blueprint(admin)
    app.register_blueprint(items)

    with app.app_context():
        db.create_all()

    return app

