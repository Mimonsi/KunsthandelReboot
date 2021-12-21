from flask import Blueprint, render_template
from flask_babel import gettext

from kunsthandel.main.utils import role_required
from kunsthandel.models import Role, Item, Origin, Image

main = Blueprint("main", __name__)


@main.route("/")
@main.route("/home")
@role_required(Role.Visitor)
def home():
    full_text = gettext("Currently there are %(items)s items from %(origins)s origins. %(images)s pictures have been uploaded.", items=Item.query.count(), origins=Origin.query.count(), images=Image.query.count())
    return render_template("home.html", text=full_text)
