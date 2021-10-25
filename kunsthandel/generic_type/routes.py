from flask import Blueprint, render_template, url_for, request, abort
from flask_babel import gettext

from kunsthandel.main.utils import role_required
from kunsthandel.models import Item, Image, Role, Type, Location, Origin

generic_type = Blueprint('generic_type', __name__)


@generic_type.route('/<string:model_name>/')
@generic_type.route('/<string:model_name>/overview')
@role_required(Role.User)
def overview(model_name):
    page = request.args.get('page', type=int)
    global model
    if model_name == "types":
        model = Type.query.paginate(page=page, per_page=50)
    elif model_name == "locations":
        model = Location.query.paginate(page=page, per_page=50)
    elif model_name == "origins":
        model = Origin.query.paginate(page=page, per_page=50)
    else:
        abort(404)
    return render_template("generic_type.html", title=gettext("Overview:"), model=model, model_name=model_name)


@generic_type.route('/<string:model_name>/create')
def create(model_name):
    pass


@generic_type.route('/<string:model_name>/<int:id>/edit')
def edit(model_name, id):
    pass


@generic_type.route('/<string:model_name>/<int:id>')
def details(model_name, id):
    pass