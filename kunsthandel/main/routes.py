from flask import Blueprint, render_template

from kunsthandel.main.utils import role_required
from kunsthandel.models import Role

main = Blueprint("main", __name__)


@main.route("/")
@main.route("/home")
@role_required(Role.Visitor)
def home():
    return render_template("home.html")
