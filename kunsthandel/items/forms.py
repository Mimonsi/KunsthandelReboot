from flask_babel import lazy_gettext
from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import StringField, SubmitField, MultipleFileField
from wtforms_sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, Length

from kunsthandel.models import Type, Location, Origin


class EditItemForm(FlaskForm):
    name = StringField(lazy_gettext('Name*'), validators=[DataRequired(), Length(min=2, max=50)])
    type = QuerySelectField(lazy_gettext('Type'), query_factory=lambda: Type.query.all(), get_label="name", allow_blank=True)
    location = QuerySelectField(lazy_gettext('Location'), query_factory=lambda: Location.query.all(), get_label="name", allow_blank=True)
    origin = QuerySelectField(lazy_gettext('Origin'), query_factory=lambda: Origin.query.all(), get_label="name", allow_blank=True)
    size = StringField(lazy_gettext('Size'), validators=[Length(max=50)])
    comment = StringField(lazy_gettext('Comment'))

    thumbnail = FileField(lazy_gettext('Upload thumbnail'))
    images = MultipleFileField(lazy_gettext('Upload images')) # validators=[FileAllowed(['jpg', 'png'])]

    submit = SubmitField(lazy_gettext('Create'))
