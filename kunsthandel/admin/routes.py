from flask import Blueprint, render_template, flash, redirect, url_for, current_app, request

from kunsthandel.admin.forms import CreateUsersForm, CreateItemsForm
from kunsthandel.admin.database_functions import create_test_items, create_test_users
from kunsthandel.main.utils import role_required, create_qr_code
from kunsthandel.models import Role, Item

admin = Blueprint('admin', __name__)


@admin.route('/admin/home', methods=['GET', 'POST'])
@admin.route('/admin/', methods=['GET', 'POST'])
@role_required(Role.Administrator)
def home():
    create_user_form = CreateUsersForm()
    if create_user_form.validate_on_submit():
        users_created = create_test_users(create_user_form.account_amount.data, create_user_form.password.data)
        flash("Successfully created " + str(users_created) + " User Accounts.", "success")

    create_items_form = CreateItemsForm()
    if create_items_form.validate_on_submit():
        datasets_created = create_test_items(item_amount=create_items_form.item_amount.data, type_amount=create_items_form.type_amount.data,
                                          location_amount=create_items_form.location_amount.data, origin_amount=create_items_form.origin_amount.data)
        flash("Successfully created " + str(datasets_created) + " Datasets.", "success")
    return render_template("admin/home.html", create_user_form=create_user_form, create_items_form=create_items_form)


@admin.route('/create_items_and_users')
def create_items_and_users():
    user_amount = create_test_users()
    item_amount = create_test_items()
    flash("Created " + str(user_amount+item_amount) + " datasets!", "success")
    return redirect(url_for('main.home'))


@admin.route('/create_users', methods=['GET', 'POST'])
def create_users():
    form = CreateUsersForm()
    if form.validate_on_submit():
        amount_created = create_test_users()
        flash("Created " + str(amount_created) + " user accounts.", "success")
    if request.method == 'GET':
        pass
    return redirect(url_for('admin.home'))


@admin.route('/create_users')
def create_items():
    item_amount = create_test_items()
    flash("Created " + str(item_amount) + " item datasets!", "success")
    return redirect(url_for('main.home'))


@admin.route('/qr_printsheet')
def bulk_qr_code():
    items = Item.query.all()
    base_url = current_app.config["BASE_URL"]
    urls = []
    for item in items:
        filename = create_qr_code(item.id, base_url + "/code/" + str(item.qr_hash))
        urls.append(base_url + url_for('static', filename='qr/' + filename))
    return render_template('qrcode_printscreen.html', urls=urls)



