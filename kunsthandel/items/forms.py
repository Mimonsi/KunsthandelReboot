from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField, PasswordField, SelectField, BooleanField, IntegerField, HiddenField, \
    MultipleFileField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, EqualTo, Length, ValidationError, Optional

from kunsthandel.models import User, Role, Type, Location, Origin


class CreateItemForm(FlaskForm):
    name = StringField('Name*', validators=[DataRequired(), Length(min=2, max=50)])
    type = QuerySelectField('Type', query_factory=lambda: Type.query.all(), get_label="name", allow_blank=True)
    location = QuerySelectField('Location', query_factory=lambda: Location.query.all(), get_label="name", allow_blank=True)
    origin = QuerySelectField('Origin', query_factory=lambda: Origin.query.all(), get_label="name", allow_blank=True)
    size = StringField('Size', validators=[Length(max=50)])
    comment = StringField('Comment')

    thumbnail = FileField('Upload thumbnail')
    images = MultipleFileField('Upload images') # validators=[FileAllowed(['jpg', 'png'])]

    submit = SubmitField('Create')

    #def validate_username(self, username):
    #    existing_user = User.query.filter_by(username=username.data).first()
    #    if existing_user:
    #        raise ValidationError('This username is already taken. Please choose different one')
