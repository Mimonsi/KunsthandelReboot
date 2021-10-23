import os
import secrets
from functools import wraps

import qrcode as qrcode
from flask import abort, request, current_app

from flask_login import current_user, login_required
from flask_login.config import EXEMPT_METHODS

from kunsthandel.models import Role


def role_required(access_level: Role):  # Also implements all functionality of @login_required
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):

            if request.method in EXEMPT_METHODS:
                return func(*args, **kwargs)
            elif current_app.config.get('LOGIN_DISABLED'):
                return func(*args, **kwargs)
            elif not current_user.is_authenticated:
                return current_app.login_manager.unauthorized()
            if current_user.role_id < access_level.value:
                abort(403, "No permission to access this content")
            return func(*args, **kwargs)

        return wrapper

    return decorator


def get_qr_hash():
    return secrets.token_urlsafe(16)


def create_qr_code(id, url):
    filename = os.path.join(current_app.root_path, 'static/qr/' + str(id) + ".png")
    #qr = qrcode.make(url)
    #qr.save(filename)
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image()
    img.save(filename)
    return str(id) + ".png"
