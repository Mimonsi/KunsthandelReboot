from flask import Blueprint
from kunsthandel.main.utils import role_required
from kunsthandel.models import Role

admin = Blueprint('admin', __name__)


@admin.route('/admin/home')
@admin.route('/admin/')
@role_required(Role.Administrator)
def home():
    return "Hello, World" #TODO: Add Page




