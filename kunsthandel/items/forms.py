from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SelectField, BooleanField, IntegerField, HiddenField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, EqualTo, Length, ValidationError, Optional

from kunsthandel.models import User, Role, Type, Location, Origin


class CreateItemForm(FlaskForm):
    name = StringField('Name*', validators=[DataRequired(), Length(min=2, max=50)])
    type = QuerySelectField('Type*', query_factory=lambda: Type.query.all(), get_label="name")
    location = QuerySelectField('Location*', query_factory=lambda: Location.query.all(), get_label="name")
    origin = QuerySelectField('Origin*', query_factory=lambda: Origin.query.all(), get_label="name")
    size = StringField('Size', validators=[Length(max=50)])
    comment = StringField('Comment')



    submit = SubmitField('Create')

    """
    id = db.Column(db.Integer, primary_key=True)
    type_id = db.Column(db.Integer, db.ForeignKey('type.id'), nullable=True)
    type = db.relationship('Type', backref=db.backref('items', lazy=True))

    location_id = db.Column(db.Integer, db.ForeignKey('location.id'), nullable=True)
    location = db.relationship('Location', backref='items', lazy=True)

    origin_id = db.Column(db.Integer, db.ForeignKey('origin.id'), nullable=True)
    origin = db.relationship('Origin', backref='items', lazy=True)

    name = db.Column(db.String(255), nullable=True)

    edited_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    edited = db.relationship('User', backref='items', lazy=True)

    comment = db.Column(db.String(255), nullable=True)
    size = db.Column(db.String(255), nullable=True)
    """

    #def validate_username(self, username):
    #    existing_user = User.query.filter_by(username=username.data).first()
    #    if existing_user:
    #        raise ValidationError('This username is already taken. Please choose different one')
