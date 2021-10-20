from flask import Blueprint, request, abort, render_template, url_for, redirect, flash
from flask_login import login_required

from kunsthandel.main.test_data import create_test_users, create_test_items
from kunsthandel.main.utils import role_required
from kunsthandel.models import create_account, Role

main = Blueprint('main', __name__)


@main.route('/')
@main.route('/home')
@role_required(Role.Visitor)
def home():
    return render_template("home.html")


@main.route('/createadmin')
def create_admin():
    if len(request.args) < 2:
        abort(400)
    username = request.args.get('username')
    password = request.args.get('password')
    user = create_account(username, password, role=Role.Administrator)
    return "Account created: " + str(user)


@main.route('/createtest')
def create_test():
    user_amount = create_test_users()
    item_amount = create_test_items()
    flash("Created " + str(user_amount+item_amount) + " datasets!", "success")
    return redirect(url_for('main.home'))


@main.route('/createusers')
def create_users():
    user_amount = create_test_users()
    flash("Created " + str(user_amount) + " user accounts!", "success")
    return redirect(url_for('main.home'))


@main.route('/createitems')
def create_items():
    item_amount = create_test_items()
    flash("Created " + str(item_amount) + " item datasets!", "success")
    return redirect(url_for('main.home'))
