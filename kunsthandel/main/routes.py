from flask import Blueprint, request, abort, render_template

from kunsthandel.models import create_account, Role

main = Blueprint('main', __name__)


@main.route('/')
@main.route('/home')
def home():
    return render_template("layout.html")


@main.route('/createadmin')
def create_admin():
    if len(request.args) < 2:
        abort(400)
    username = request.args.get('username')
    password = request.args.get('password')
    user = create_account(username, password, role=Role.administrator)
    return "Account created: " + str(user)
