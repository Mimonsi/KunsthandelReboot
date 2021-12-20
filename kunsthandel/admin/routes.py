import io
import os
import time
import zipfile
from datetime import datetime

from flask import Blueprint, render_template, flash, redirect, url_for, current_app, abort, session, make_response
from flask_babel import gettext

from kunsthandel.admin.database_functions import create_test_items, create_test_users
from kunsthandel.admin.forms import CreateUsersForm, CreateItemsForm, CreateQRCodesForm
from kunsthandel.admin.storage_manager import get_database_usage, get_directory_usage
from kunsthandel.main import utils
from kunsthandel.main.utils import role_required, create_qr_code
from kunsthandel.models import Role, Item, Image

admin = Blueprint("admin", __name__)


@admin.route("/admin/home", methods=["GET"])
@admin.route("/admin", methods=["GET"])
@role_required(Role.Administrator)
def home():
    status_code = 200
    if session.get("redirect_user_form"):
        create_user_form = CreateUsersForm(data=session.get("redirect_user_form"))
        create_user_form.validate()
        session.pop("redirect_user_form")
        status_code = 400
    else:
        create_user_form = CreateUsersForm()
    if session.get("redirect_items_form"):
        create_items_form = CreateItemsForm(data=session.get("redirect_items_form"))
        create_items_form.validate()
        session.pop("redirect_items_form")
        status_code = 400
    else:
        create_items_form = CreateItemsForm()
    if session.get("redirect_qr_codes_form"):
        create_qr_codes_form = CreateQRCodesForm(data=session.get("redirect_qr_codes_form"))
        create_qr_codes_form.validate()
        session.pop("redirect_qr_codes_form")
        status_code = 400
    else:
        create_qr_codes_form = CreateQRCodesForm()
    return render_template("admin/home.html", title=gettext("Administration"), create_user_form=create_user_form,
                           create_items_form=create_items_form, create_qr_codes_form=create_qr_codes_form), status_code


@admin.route("/admin/fullbackup", methods=["GET"])
@role_required(Role.Administrator)
def full_backup():
    fileobj = io.BytesIO()
    paths = [(current_app.config.get("STORAGE_DATABASE_FILE"), os.path.join(current_app.root_path, current_app.config.get("STORAGE_DATABASE_FILE")))]
    media_dir = os.path.join(current_app.root_path, f"static/{current_app.config.get('MEDIA_ROOT_PATH')}/images/")
    image_objects = Image.query.all()
    for image_object in image_objects:
        paths.append((image_object.path, media_dir + image_object.path))
    with zipfile.ZipFile(fileobj, "w") as zip_file:
        for path in paths:
            zip_info = zipfile.ZipInfo(path[1])
            zip_info.filename = path[0]
            zip_info.date_time = time.localtime(time.time())[:6]
            zip_info.compress_type = zipfile.ZIP_DEFLATED
            with open(path[1], "rb") as fd:
                zip_file.writestr(zip_info, fd.read())
    fileobj.seek(0)

    response = make_response(fileobj.read())
    response.headers.set("Content-Type", "zip")
    time_string = datetime.now().strftime("%d.%m.%y_%H:%M")
    response.headers.set("Content-Disposition", "attachment", filename=f"backup_full_{time_string}.zip")
    return response


@admin.route("/admin/create_users", methods=["POST"])
@role_required(Role.Administrator)
def create_users():
    form = CreateUsersForm()
    if form.validate_on_submit():
        amount = create_test_users(form.account_amount.data, form.password.data)
        flash(gettext("Successfully created %s user accounts.") % str(amount), "success")
        return redirect(url_for("admin.home"))
    else:
        session["redirect_user_form"] = form.data
        return redirect(url_for("admin.home"))


@admin.route("/admin/create_items", methods=["POST"])
@role_required(Role.Administrator)
def create_items():
    form = CreateItemsForm()
    if form.validate_on_submit():
        amount = create_test_items(item_amount=form.item_amount.data, type_amount=form.type_amount.data,
                                   location_amount=form.location_amount.data, origin_amount=form.origin_amount.data)
        flash(gettext("Successfully created %s datasets.") % str(amount), "success")
        return redirect(url_for("admin.home"))
    else:
        session["redirect_items_form"] = form.data
        return redirect(url_for("admin.home"))


@admin.route("/admin/qr_printsheet", methods=["POST"])
@role_required(Role.Administrator)
def qr_printsheet():
    form = CreateQRCodesForm()
    if form.validate_on_submit():
        items = Item.query.all()
        base_url = current_app.config["BASE_URL"]
        urls = []
        for item in items:
            filename = create_qr_code(item.id, f"{base_url}/code/{item.qr_hash}", version=form.code_version.data,
                                      box_size=form.code_size.data, border=form.code_border_size.data)
            urls.append(base_url + url_for("static", filename=f"{current_app.config['MEDIA_ROOT_PATH']}/qr/{filename}"))
        return render_template("qrcode_printscreen.html", urls=urls)
    else:
        session["redirect_qr_codes_form"] = form.data
        flash(gettext("Something went wrong. This is awkward..."), "danger")
        return redirect(url_for("admin.home"))


@admin.route("/admin/storage_overview", methods=["GET"])
@role_required(Role.Administrator)
def storage_overview():
    database_usage = get_database_usage()
    all = [database_usage, get_directory_usage(local_path="static/texts", name="Texts"),
           get_directory_usage(local_path="static/qr", name="QR Codes"),
           get_directory_usage(local_path="static/images", name="Images")]

    total = 0
    for single in all:
        total += single[3]
    all.append((gettext("Total"), "", utils.format_filesize(total), total))
    return render_template("admin/storage_overview.html", title=gettext("Storage management"), all=all)


@admin.route("/admin/403")
@role_required(Role.Administrator)
def error_403():
    abort(403)


@admin.route("/admin/404")
@role_required(Role.Administrator)
def error_404():
    abort(404)


@admin.route("/admin/500")
@role_required(Role.Administrator)
def error_500():
    abort(500)
