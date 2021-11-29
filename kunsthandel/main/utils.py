import os
from functools import wraps

import qrcode as qrcode
from PIL import Image
from flask import abort, request, current_app
from flask_babel import format_decimal

from flask_login import current_user
from flask_login.config import EXEMPT_METHODS
from werkzeug.datastructures import FileStorage

import kunsthandel.models
from kunsthandel import db
from kunsthandel.models import Role, Item, Image as Model_image


def role_required(access_level: Role):
    # Also implements all functionality of @login_required
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):

            if request.method in EXEMPT_METHODS:  # pragma: no cover
                return func(*args, **kwargs)
            elif current_app.config.get("LOGIN_DISABLED"):
                return func(*args, **kwargs)
            elif not current_user.is_authenticated:
                return current_app.login_manager.unauthorized()
            if current_user.role_id < access_level.value:
                abort(403, "No permission to access this content")
            return func(*args, **kwargs)

        return wrapper

    return decorator


def create_qr_code(id, url, version, box_size, border):
    dir_path = os.path.join(current_app.root_path, f"static/{current_app.config['MEDIA_ROOT_PATH']}/qr/")
    os.makedirs(dir_path, exist_ok=True)
    filename = os.path.join(current_app.root_path, f"static/{current_app.config['MEDIA_ROOT_PATH']}/qr/{id}.png")
    # qr = qrcode.make(url)
    # qr.save(filename)
    qr = qrcode.QRCode(version=version, box_size=box_size, border=border)  # 1, 10, 5
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image()
    img.save(filename)
    return f"{id}.png"


def format_filesize(bytes):
    steps = [" B", " KB", " MB", " GB", " TB", " PB"]
    steps_done = 0
    number = bytes
    while number > 1000:
        steps_done += 1
        number /= 1024
    number = round(number, 2)
    return format_decimal(number) + steps[steps_done]


def save_thumbnail(thumbnail: FileStorage, item: Item):
    # Remove old thumbnail(s)
    previous_thumbnails = Model_image.query.filter_by(item=item, is_thumbnail=True).all()
    for t in previous_thumbnails:
        t.is_thumbnail = False

    saved_thumbnail = save_images([thumbnail], item)[0]  # Only one image is saved and returned
    saved_thumbnail.is_thumbnail = True
    db.session.commit()


def save_images(form_images, item):
    image_objects = []
    index = Model_image.query.count()
    dir_path = os.path.join(current_app.root_path, f"static/{current_app.config['MEDIA_ROOT_PATH']}/images/{item.id}/")
    os.makedirs(dir_path, exist_ok=True)
    for form_image in form_images:
        if form_image.filename == "":  # pragma: no cover This covers the case of no files being attached
            continue
        _, f_ext = os.path.splitext(form_image.filename)  # _ -> Throws away value, not needed
        picture_fn = str(index) + f_ext
        picture_path = os.path.join(current_app.root_path, f"static/{current_app.config['MEDIA_ROOT_PATH']}/images/{item.id}/", picture_fn)

        # output_size = (125, 125)
        i = Image.open(form_image)
        # i.thumbnail(output_size)  # Resize image to displayed size

        i.save(picture_path)
        database_path = f"{item.id}/{index}{f_ext}"
        image_object = kunsthandel.models.Image(path=database_path, item=item)
        image_objects.append(image_object)
        db.session.add(image_object)
        index += 1
    db.session.commit()
    return image_objects
