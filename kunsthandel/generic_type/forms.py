from flask_babel import gettext
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length


class EditGenericTypeForm(FlaskForm):
    name = StringField(gettext('Name*'), validators=[DataRequired(), Length(min=2, max=50)])

    submit = SubmitField(gettext('Create'))
