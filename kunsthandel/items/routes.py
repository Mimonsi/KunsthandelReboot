from flask import Blueprint, request, render_template, url_for, flash, redirect, current_app
from flask_babel import gettext
from flask_login import current_user

from kunsthandel import db
from kunsthandel.items.forms import EditItemForm
from kunsthandel.main.utils import role_required, save_images, save_thumbnail, create_qr_code
from kunsthandel.models import Role, Item, Image

items = Blueprint("items", __name__)


@items.route("/code/<string:hash>", methods=["GET"])
def token(hash):
    item = Item.query.filter_by(qr_hash=hash).first_or_404()
    return render_template("items/item.html", title=gettext("Item details %s") % str(id), item=item)


@items.route("/items", methods=["GET"])
@role_required(Role.User)
def overview():
    page = request.args.get("page", type=int)
    items = Item.query.paginate(page=page, per_page=50)
    return render_template("items/items.html", title=gettext("Item overview"), items=items)


@items.route("/items/<int:id>", methods=["GET"])
@role_required(Role.User)
def details(id):
    item = Item.query.get_or_404(id)
    return render_template("items/item.html", title=gettext("Item details %s") % str(id), item=item)


@items.route("/items/<int:id>/code", methods=["GET"])
@role_required(Role.User)
def code(id):
    item = Item.query.get_or_404(id)
    base_url = current_app.config["BASE_URL"]
    filename = create_qr_code(item.id, f"{base_url}/code/{item.qr_hash}")
    urls = [base_url + url_for("static", filename=f"{current_app.config['MEDIA_ROOT_PATH']}/qr/{filename}")]
    return render_template("qrcode_printscreen.html", urls=urls)


@items.route("/items/create", methods=["GET", "POST"])
@role_required(Role.Editor)
def create():
    form = EditItemForm()
    if request.method == "POST":
        if form.validate_on_submit():
            item = Item(name=form.name.data, type=form.type.data, location=form.location.data, origin=form.origin.data, size=form.size.data, comment=form.comment.data, edited=current_user)
            db.session.add(item)
            db.session.commit()
            if form.thumbnail.data:
                save_thumbnail(form.thumbnail.data, item)
            if form.images.data:
                save_images(form.images.data, item)
            flash(gettext("Item with ID %s successfully created") % str(item.id), "success")
            return redirect(url_for("items.overview"))
        else:
            return render_template("items/item_edit.html", title=gettext("Create new item"), form=form), 400
    else:  # GET
        return render_template("items/item_edit.html", title=gettext("Create new item"), form=form)


@items.route("/items/<int:id>/edit", methods=["GET", "POST"])
@role_required(Role.Editor)
def edit(id):
    item = Item.query.get_or_404(id)
    form = EditItemForm()
    form.submit.label.text = gettext("Update")
    if request.method == "POST":
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
            item.edited = current_user
            db.session.commit()
            flash(gettext("Item with ID %s successfully updated") % str(item.id), "success")
            return redirect(url_for("items.overview"))
        else:
            return render_template("items/item_edit.html", title=gettext("Edit item %s") % str(id), form=form, item=item), 400
    else:  # GET
        item = Item.query.get_or_404(id)
        form.name.data = item.name
        form.type.data = item.type
        form.location.data = item.location
        form.origin.data = item.origin
        form.size.data = item.size
        form.comment.data = item.comment
        return render_template("items/item_edit.html", title=gettext("Edit item %s") % str(id), form=form, item=item)


@items.route("/items/<int:id>/delete", methods=["POST"])
@role_required(Role.Editor)
def delete(id):
    item = Item.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    flash(gettext("The item has been deleted successfully"), "success")
    return redirect(url_for("items.overview"))


@items.route("/items/<int:id>/images/<int:image_id>/delete", methods=["POST"])
@role_required(Role.Editor)
def delete_image(id, image_id):
    image = Image.query.get_or_404(image_id)
    db.session.delete(image)
    db.session.commit()
    flash(gettext("The image has been deleted successfully"), "success")
    return redirect(url_for("items.edit", id=id))
