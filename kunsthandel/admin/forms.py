from flask_babel import gettext, lazy_gettext
from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField, PasswordField, FormField
from wtforms.validators import DataRequired, EqualTo


class CreateUsersForm(FlaskForm):
    account_amount = IntegerField(lazy_gettext('Number of accounts to create (0 for random)'), default=0)
    password = PasswordField(lazy_gettext('Password for all accounts'), validators=[DataRequired()])
    confirm_password = PasswordField(lazy_gettext('Confirm password'), validators=[DataRequired(), EqualTo("password")])

    submit = SubmitField(lazy_gettext('Create user accounts'))


class CreateItemsForm(FlaskForm):
    item_amount = IntegerField(lazy_gettext('Number of items to create (0 for random)'), default=0)

    type_amount = IntegerField(lazy_gettext('Number of types to create'), validators=[DataRequired()], default=5)

    location_amount = IntegerField(lazy_gettext('Number of locations to create'), validators=[DataRequired()], default=20)

    origin_amount = IntegerField(lazy_gettext('Number of origins to create'), validators=[DataRequired()], default=10)

    submit = SubmitField(lazy_gettext('Create items and constraints'))


class CreateQRCodesForm(FlaskForm):
    code_version = IntegerField(lazy_gettext('QR Code Version'), default=1)
    code_size = IntegerField(lazy_gettext('QR Code Size'), default=10)
    code_border_size = IntegerField(lazy_gettext('QR Code Border Size'), default=5)

    submit = SubmitField(lazy_gettext('Create QR codes'))
