from gettext import gettext

from flask import Blueprint, flash, redirect, url_for, render_template

from kunsthandel import db
from kunsthandel.main.utils import role_required, delete_images
from kunsthandel.models import Role, Image

images = Blueprint("images", __name__)


@images.route("/images/<int:id>", methods=["GET"])
@role_required(Role.User)
def details(id):
    image = Image.query.get_or_404(id)
    return render_template("images/image.html", image=image)


@images.route("/images/<int:id>/delete", methods=["POST"])
@role_required(Role.Editor)
def delete(id):
    image = Image.query.get_or_404(id)
    item_id = image.item_id
    delete_images([image.path])
    db.session.delete(image)
    db.session.commit()
    flash(gettext("The image has been deleted successfully"), "success")
    return redirect(url_for("items.edit", id=item_id))
