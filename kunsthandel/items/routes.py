import bdb

from flask import Blueprint, request, abort, render_template, url_for, flash, redirect
from flask_babel import gettext
from flask_login import login_required, current_user

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
    return render_template("items/item.html", title="Item Details - " + str(id), item=item, thumbnail=thumbnail,
                           images=images)


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
                    size=form.size.data, comment=form.comment.data, qr_hash=get_qr_hash(), edited=current_user)
        db.session.add(item)
        db.session.commit()
        if form.thumbnail.data:
            save_thumbnail(form.thumbnail.data, item)
        if form.images.data:
            save_images(form.images.data, item)
        flash(gettext("Item with ID %s successfully created") % str(item.id), "success")
        return redirect(url_for("items.overview"))
    return render_template("items/create_item.html", title="Create new Item", form=form)


@items.route('/items/<int:id>/edit', methods=['GET', 'POST'])
@role_required(Role.Editor)
def edit_item(id):
    item = Item.query.get_or_404(id)
    form = CreateItemForm()
    form.submit.label.text = gettext("Update")
    if form.validate_on_submit():
        if form.thumbnail.data:
            save_thumbnail(form.thumbnail.data, item)
        if form.images.data:
            save_images(form.images.data, item)
        item.name = form.name.data
        item.type = form.type.data
        item.location = form.location.data
        item.origin = form.origin.data
        item.size = form.size.data
        item.comment = form.comment.data
        flash(gettext("Item with ID %s successfully updated") % str(item.id), "success")
        return redirect(url_for("items.overview"))
    if request.method == 'GET':
        item = Item.query.get_or_404(id)
        form.name.data = item.name
        form.type.data = item.type
        form.location.data = item.location
        form.origin.data = item.origin
        form.size.data = item.size
        form.comment.data = item.comment
        return render_template("items/create_item.html", title="Edit Item " + str(id), form=form, item=item)
    return render_template("items/create_item.html", title="Create new Item", form=form)


@items.route('/items/<int:id>/delete', methods=['POST'])
@role_required(Role.Editor)
def delete_item(id):
    item = Item.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    flash(gettext("This item has been deleted"), "success")
    return redirect(url_for("items.overview"))