from functools import wraps
from flask import abort, request, current_app

from flask_login import current_user, login_required
from flask_login.config import EXEMPT_METHODS

from kunsthandel.models import Role


def role_required(access_level: Role): # Also implements all functionality of @login_required
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
