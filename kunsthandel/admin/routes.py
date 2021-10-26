from flask import Blueprint, render_template, flash, redirect, url_for, current_app, request, abort
from flask_babel import gettext

from kunsthandel.admin.forms import CreateUsersForm, CreateItemsForm, CreateQRCodesForm
from kunsthandel.admin.database_functions import create_test_items, create_test_users
from kunsthandel.admin.storage_manager import get_database_usage, get_directory_usage
from kunsthandel.main import utils
from kunsthandel.main.utils import role_required, create_qr_code
from kunsthandel.models import Role, Item

admin = Blueprint('admin', __name__)


@admin.route('/admin/home', methods=['GET', 'POST'])
@admin.route('/admin/', methods=['GET', 'POST'])
@role_required(Role.Administrator)
def home():
    create_user_form = CreateUsersForm()
    create_items_form = CreateItemsForm()
    create_qr_codes_form = CreateQRCodesForm()
    return render_template("admin/home.html", title=gettext("Administration"), create_user_form=create_user_form, create_items_form=create_items_form, create_qr_codes_form=create_qr_codes_form)


@admin.route('/admin/create_users', methods=['POST'])
@role_required(Role.Administrator)
def create_users():
    form = CreateUsersForm()
    if form.validate_on_submit():
        amount = create_test_users(form.account_amount.data, form.password.data)
        flash(gettext("Successfully created %s user accounts.") % str(amount), "success")
    return redirect(url_for('admin.home'))


@admin.route('/admin/create_items', methods=['POST'])
@role_required(Role.Administrator)
def create_items():
    form = CreateItemsForm()
    if form.validate_on_submit():
        amount = create_test_items(item_amount=form.item_amount.data, type_amount=form.type_amount.data,
                                             location_amount=form.location_amount.data,
                                             origin_amount=form.origin_amount.data)
        flash(gettext("Successfully created %s datasets.") % str(amount), "success")
    return redirect(url_for('admin.home'))


@admin.route('/admin/qr_printsheet', methods=['POST'])
@role_required(Role.Administrator)
def qr_printsheet():
    form = CreateQRCodesForm()
    if form.validate_on_submit():
        items = Item.query.all()
        base_url = current_app.config["BASE_URL"]
        urls = []
        for item in items:
            filename = create_qr_code(item.id, base_url + "/code/" + str(item.qr_hash), version=form.code_version.data,
                                      box_size=form.code_size.data, border=form.code_border_size.data)
            urls.append(base_url + url_for('static', filename='qr/' + filename))
        return render_template('qrcode_printscreen.html', urls=urls)
    flash(gettext("Something went wrong. This is awkward..."), "danger")
    return redirect(url_for('admin.home'))


@admin.route('/admin/storage_overview')
@role_required(Role.Administrator)
def storage_overview():
    database_usage = get_database_usage()
    all = [database_usage]
    all.append(get_directory_usage(local_path="static/texts", name="Texts"))
    all.append(get_directory_usage(local_path="static/qr", name="QR Codes"))
    all.append(get_directory_usage(local_path="static/images", name="Images"))

    total = 0
    for single in all:
        total += single[3]
    all.append((gettext("Total"), "", utils.format_filesize(total), total))
    return render_template('admin/storage_overview.html', title=gettext("Storage management"), all=all)

