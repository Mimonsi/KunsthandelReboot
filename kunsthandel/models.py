from enum import Enum

import flask_bcrypt
from flask_login import UserMixin
from flask import current_app
from flask_login import UserMixin
from kunsthandel import db, login_manager


class Role(Enum):
    external = 0
    visitor = 1
    user = 2
    editor = 3
    administrator = 4


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    role_id = db.Column(db.Integer, nullable=False, default=0) # 0 = No role, unauthorized

    # role could also be used as external table with foreign key, but roles are hard-coded 0 < 1 < 2 < 3 < 4
    def __repr__(self):
        return f"User('{self.username}, '{self.role_id}')"


def create_account(username, password, role):
    hashed_password = flask_bcrypt.generate_password_hash(password).decode('utf-8')
    new_account = User(username=username, password=hashed_password, role_id=role.value)
    db.session.add(new_account)
    db.session.commit()
    return new_account