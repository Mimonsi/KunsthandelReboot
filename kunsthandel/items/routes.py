from flask import Blueprint, request, abort, render_template, url_for
from flask_login import login_required

from kunsthandel.main.utils import role_required
from kunsthandel.models import create_account, Role, Item

items = Blueprint('items', __name__)


@items.route('/items')
@items.route('/items/overview')
@role_required(Role.User)
def overview():
    page = request.args.get('page', type=int)
    items = Item.query.paginate(page=page, per_page=50)
    return render_template("items/items.html", title='Item Overview', items=items)


@items.route('/items/<int:id>')
def item_details(id):
    item = Item.query.get_or_404(id)
    thumbnail = url_for('static', filename='images/default.jpg')  # TODO: Replace with correct logic

    gallery = item.gallery
    images = gallery.images
    if len(gallery.images) > 0:
        first_picture = gallery.images[0]
        thumbnail = url_for('static', filename='images/' + first_picture.path)
    return render_template("items/item.html", title="Item Details - " + str(id), item=item, thumbnail=thumbnail, images=images)

