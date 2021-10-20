from flask import Blueprint, request, abort, render_template
from flask_login import login_required

from kunsthandel.main.utils import role_required
from kunsthandel.models import create_account, Role, Item

items = Blueprint('items', __name__)


@items.route('/items')
@items.route('/items/overview')
@role_required(Role.User)
def overview():
    page = request.args.get('page', type=int)
    items = Item.query.paginate(page=page, per_page=5)
    return render_template("items/items.html", title='Item Overview', items=items)

