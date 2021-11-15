from enum import Enum

import flask_bcrypt
from flask_login import UserMixin
from flask import current_app, url_for
from flask_login import UserMixin
from sqlalchemy.orm import relationship

from kunsthandel import db, login_manager


class Role(Enum):
    External = 0
    Visitor = 1
    User = 2
    Editor = 3
    Administrator = 4


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    locale = db.Column(db.String(2), nullable=False, default="en")
    role_id = db.Column(db.Integer, nullable=False, default=0)  # 0 = No role, unauthorized

    # role could also be used as external table with foreign key, but roles are hard-coded 0 < 1 < 2 < 3 < 4
    def __repr__(self):
        return f'<User> (username={self.username}, role_id={self.role_id})'

    def role(self):
        return Role(self.role_id).name

    def has_permission(self, level: int):
        return self.role_id >= level


class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f'<Location> (id={self.id}, name={self.name})'

    def model_name(self):
        return "Location"


class Origin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f'<Origin> (id={self.id}, name={self.name})'

    def model_name(self):
        return "Origin"


class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String, nullable=False)
    is_thumbnail = db.Column(db.Boolean, nullable=False, default=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=True)
    item = db.relationship('Item', backref='images', lazy=True)

    # item = db.relationship('Item', lazy=True)

    def __repr__(self):
        return f'<Image> (id={self.id}, path={self.path}, item_id={self.item_id}, is_thumbnail={self.is_thumbnail})'

    def url(self):
        return url_for('static', filename='images/' + self.path)


class Type(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f'<Type> (id={self.id}, name={self.name})'

    def model_name(self):
        return "Type"


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=True)

    type_id = db.Column(db.Integer, db.ForeignKey('type.id'), nullable=True)
    type = db.relationship('Type', backref=db.backref('items', lazy=True))

    location_id = db.Column(db.Integer, db.ForeignKey('location.id'), nullable=True)
    location = db.relationship('Location', backref='items', lazy=True)

    origin_id = db.Column(db.Integer, db.ForeignKey('origin.id'), nullable=True)
    origin = db.relationship('Origin', backref='items', lazy=True)

    edited_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    edited = db.relationship('User', backref='items', lazy=True)

    comment = db.Column(db.String(255), nullable=True)
    size = db.Column(db.String(255), nullable=True)

    qr_hash = db.Column(db.String(32), nullable=False)

    def __repr__(self):
        return f'<Item> (id={self.id}, name={self.name}, type={self.type}, location={self.location}, origin={self.origin})'

    def images(self):
        return Image.query.filter_by(item_id=self.id).all()

    def thumbnail(self):
        thumbnail = Image.query.filter_by(item_id=self.id, is_thumbnail=True).first()
        return thumbnail


def create_account(username, password, role):
    hashed_password = flask_bcrypt.generate_password_hash(password).decode('utf-8')
    new_account = User(username=username, password=hashed_password, role_id=role.value)
    db.session.add(new_account)
    db.session.commit()
    return new_account
