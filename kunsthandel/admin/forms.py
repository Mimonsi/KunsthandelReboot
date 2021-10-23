from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField, PasswordField
from wtforms.validators import DataRequired, EqualTo


class CreateUsersForm(FlaskForm):
    account_amount = IntegerField('Number of accounts to create (0 for random)', default=0)
    password = PasswordField('Password for all accounts', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm password', validators=[DataRequired(), EqualTo("password")])

    submit = SubmitField('Create user accounts')


class CreateItemsForm(FlaskForm):
    pass
    item_amount = IntegerField('Number of items to create (0 for random)', default=0)

    type_amount = IntegerField('Number of types to create', validators=[DataRequired()], default=5)

    location_amount = IntegerField('Number of locations to create', validators=[DataRequired()], default=20)

    origin_amount = IntegerField('Number of origins to create', validators=[DataRequired()], default=10)

    submit = SubmitField('Create items and constraints')
    #password = PasswordField('Password for all accounts')
    #confirm_password = PasswordField('Confirm password', validators=[EqualTo("password")])

    #submit = SubmitField('Create user accounts')