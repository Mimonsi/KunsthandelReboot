from gettext import gettext

from flask import Blueprint, render_template

from kunsthandel.main.utils import role_required
from kunsthandel.models import Role, Item, Origin, Image

main = Blueprint("main", __name__)


@main.route("/")
@main.route("/home")
@role_required(Role.Visitor)
def home():
    full_text = f"Currently there are {Item.query.count()} items from {Origin.query.count()} origins. {Image.query.count()} pictures have been uploaded."
    # ??? TODO: Die Übersetzung funktioniert hier nicht aus irgendeinem Grund...?
    return render_template("home.html", text=full_text)
