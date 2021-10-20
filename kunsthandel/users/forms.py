from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SelectField, BooleanField, IntegerField, HiddenField
from wtforms.validators import DataRequired, EqualTo, Length, ValidationError

from kunsthandel.models import User, Role


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')

    submit = SubmitField('Login')


class CreateAccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])#
    role = SelectField('Role', choices=[(r.value, r.name) for r in Role])

    submit = SubmitField('Create')

    def validate_username(self, username):
        existing_user = User.query.filter_by(username=username.data).first()
        if existing_user:
            raise ValidationError('This username is already taken. Please choose different one')


class UpdateOwnAccountForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])#

    submit = SubmitField('Update')


class UpdateAccountForm(FlaskForm):
    old_username = HiddenField() # Empty data if new account
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password')
    confirm_password = PasswordField('Confirm Password', validators=[EqualTo('password')])#
    role = SelectField('Role', choices=[(r.value, r.name) for r in Role])

    submit = SubmitField('Update')

    def validate_username(self, username):
        existing_user = User.query.filter_by(username=username.data).first()
        if existing_user and username.data != self.old_username.data: # Check if old username saved in hidden field is the same
            raise ValidationError('This username is already taken. Please choose different one')
