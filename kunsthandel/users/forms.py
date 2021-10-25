from flask_babel import gettext, lazy_gettext
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SelectField, BooleanField, IntegerField, HiddenField
from wtforms.validators import DataRequired, EqualTo, Length, ValidationError

from kunsthandel.models import User, Role


class LoginForm(FlaskForm):
    username = StringField(lazy_gettext('Username'), validators=[DataRequired()])
    password = PasswordField(lazy_gettext('Password'), validators=[DataRequired()])
    remember = BooleanField(lazy_gettext('Remember Me'))

    submit = SubmitField(lazy_gettext('Login'))


class CreateAccountForm(FlaskForm):
    username = StringField(lazy_gettext('Username*'), validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField(lazy_gettext('Password*'), validators=[DataRequired()])
    confirm_password = PasswordField(lazy_gettext('Confirm Password*'), validators=[DataRequired(), EqualTo('password')])#
    role = SelectField(lazy_gettext('Role*'), choices=[(r.value, r.name) for r in Role])
    locale = SelectField(lazy_gettext('Locale*'), validators=[DataRequired()],
                         choices=[("en", "English"), ("de", "Deutsch")], default=("en", "English"))

    submit = SubmitField(lazy_gettext('Create'))

    def validate_username(self, username):
        existing_user = User.query.filter_by(username=username.data).first()
        if existing_user:
            raise ValidationError(lazy_gettext('This username is already taken. Please choose different one'))


class UpdateOwnAccountForm(FlaskForm):
    password = PasswordField(lazy_gettext('Password'), validators=[DataRequired()])
    confirm_password = PasswordField(lazy_gettext('Confirm Password'), validators=[DataRequired(), EqualTo('password')])#
    locale = SelectField(lazy_gettext('Locale*'), validators=[DataRequired()], choices=[("en", "English"), ("de", "Deutsch")], default=("en", "English"))

    submit = SubmitField(lazy_gettext('Update'))


class UpdateAccountForm(FlaskForm):
    old_username = HiddenField() # Empty data if new account
    username = StringField(lazy_gettext('Username'), validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField(lazy_gettext('Password'))
    confirm_password = PasswordField(lazy_gettext('Confirm Password'), validators=[EqualTo('password')])#
    role = SelectField(lazy_gettext('Role'), choices=[(r.value, r.name) for r in Role])
    locale = SelectField(lazy_gettext('Locale*'), validators=[DataRequired()],
                         choices=[("en", "English"), ("de", "Deutsch")], default=("en", "English"))

    submit = SubmitField(lazy_gettext('Update'))

    def validate_username(self, username):
        existing_user = User.query.filter_by(username=username.data).first()
        if existing_user and username.data != self.old_username.data: # Check if old username saved in hidden field is the same
            raise ValidationError(gettext('This username is already taken. Please choose different one'))
