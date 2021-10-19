from flask import Blueprint, render_template, request
from flask_login import login_required

from kunsthandel.models import User

admin = Blueprint('admin', __name__)


@admin.route('/admin/users')
@login_required
def accounts_overview():
    page = request.args.get('page', type=int)
    users = User.query.paginate(page=page, per_page=5)
    return render_template("account_overview.html", title='Manage User Accounts', users=users)
