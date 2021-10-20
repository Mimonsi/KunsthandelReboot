from enum import Enum

import flask_bcrypt
from flask_login import UserMixin
from flask import current_app
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
    role_id = db.Column(db.Integer, nullable=False, default=0) # 0 = No role, unauthorized

    # role could also be used as external table with foreign key, but roles are hard-coded 0 < 1 < 2 < 3 < 4
    def __repr__(self):
        return f"User('{self.username}, '{self.role_id}')"

    def role(self):
        return Role(self.role_id).name

    def has_permission(self, level: int):
        return self.role_id >= level


class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)


class Origin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)


class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String, nullable=False)
    gallery_id = db.Column(db.Integer, db.ForeignKey('gallery.id'), nullable=True)
    gallery = db.relationship('Gallery', backref='images', lazy=True)


class Type(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return '<Type %r>' % self.name


class Gallery(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return '<Type %r>' % self.name


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type_id = db.Column(db.Integer, db.ForeignKey('type.id'), nullable=True)
    type = db.relationship('Type', backref=db.backref('items', lazy=True))

    location_id = db.Column(db.Integer, db.ForeignKey('location.id'), nullable=True)
    location = db.relationship('Location', backref='items', lazy=True)

    origin_id = db.Column(db.Integer, db.ForeignKey('origin.id'), nullable=True)
    origin = db.relationship('Origin', backref='items', lazy=True)

    name = db.Column(db.String(255), nullable=True)
    gallery_id = db.Column(db.Integer, db.ForeignKey('gallery.id'), nullable=True)
    gallery = db.relationship('Gallery', backref='items', lazy=True)

    edited_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    edited = db.relationship('User', backref='items', lazy=True)

    comment = db.Column(db.String(255), nullable=True)
    size = db.Column(db.String(255), nullable=True)
    # Maybe add hashlink for QR codes here

    def __repr__(self):
        return '<Item %r>' % self.name


def create_account(username, password, role):
    hashed_password = flask_bcrypt.generate_password_hash(password).decode('utf-8')
    new_account = User(username=username, password=hashed_password, role_id=role.value)
    db.session.add(new_account)
    db.session.commit()
    return new_account