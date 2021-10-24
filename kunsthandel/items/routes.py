import bdb

from flask import Blueprint, request, abort, render_template, url_for, flash, redirect
from flask_login import login_required

from kunsthandel import db
from kunsthandel.items.forms import CreateItemForm
from kunsthandel.main.utils import role_required, save_images, get_qr_hash, save_thumbnail
from kunsthandel.models import create_account, Role, Item, Image

items = Blueprint('items', __name__)


@items.route('/code/<string:hash>')
def token(hash):
    item = Item.query.filter_by(qr_hash=hash).first_or_404()

    thumbnail = url_for('static', filename='images/default.jpg')  # TODO: Replace with correct logic
    images = Image.query.filter_by(item_id=item.id).all()
    if len(images) > 0:
        first_picture = Image.query.filter_by(item_id=item.id, is_thumbnail=True).first()
        thumbnail = url_for('static', filename='images/' + first_picture.path)
    return render_template("items/item.html", title="Item Details - " + str(id), item=item, thumbnail=thumbnail, images=images)


@items.route('/items')
@items.route('/items/overview')
@role_required(Role.User)
def overview():
    page = request.args.get('page', type=int)
    items = Item.query.paginate(page=page, per_page=50)
    return render_template("items/items.html", title='Item Overview', items=items)


@items.route('/items/<int:id>')
@role_required(Role.User)
def item_details(id):
    item = Item.query.get_or_404(id)

    return render_template("items/item.html", title="Item Details - " + str(id), item=item)


@items.route('/items/create', methods=['GET', 'POST'])
@role_required(Role.Editor)
def create_item():
    form = CreateItemForm()
    if form.validate_on_submit():
        item = Item(name=form.name.data, type=form.type.data, location=form.location.data, origin=form.origin.data,
                    size=form.size.data, comment=form.comment.data, qr_hash=get_qr_hash())
        db.session.add(item)
        db.session.commit()
        if form.thumbnail.data:
            save_thumbnail(form.thumbnail.data, item)
        if form.images.data:
            save_images(form.images.data, item)
        flash("Item with ID " + str(item.id) + " successfully created", "success")
        return redirect(url_for("items.overview"))
    elif request.method == 'GET':
        print("Test 2")
    return render_template("items/create_item.html", title="Create new Item", form=form)


@items.route('/items/<int:id>/edit', methods=['GET', 'POST'])
@role_required(Role.Editor)
def edit_item(id):
    abort(404)
    """
    item = Item.query.get_or_404(id)
    form = EditItemForm()
    if form.validate_on_submit():
        print("Test")
    elif request.method == 'GET':
        print("Test 2")
    return render_template("items/create_item.html", title="Edit Item Details - " + str(id), item=item, form=form)
    """


@items.route('/items/<int:id>/delete')
@role_required(Role.Editor)
def delete_item(id):
    abort(404)