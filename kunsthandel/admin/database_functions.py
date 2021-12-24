import io
import os
import random
import time
import zipfile
from datetime import datetime
from shutil import copy, copyfile

from flask import current_app, make_response

from kunsthandel import db
from kunsthandel.models import create_account, Role, Location, Origin, Type, Item, Image


def create_test_items(item_amount, type_amount, location_amount, origin_amount):
    type_values = []
    location_values = []
    origin_values = []
    created = 0
    with current_app.open_resource("static/texts/types.txt", mode="rb") as t:
        type_values = t.read().decode("utf-8").splitlines()
    for i in range(0, type_amount):
        type = Type(name=type_values[random.randint(0, len(type_values) - 1)])
        db.session.add(type)
        created += 1
    with current_app.open_resource("static/texts/locations.txt", mode="rb") as l:
        location_values = l.read().decode("utf-8").splitlines()
    for i in range(0, location_amount):
        location = Location(name=location_values[random.randint(0, len(location_values) - 1)])
        db.session.add(location)
        created += 1
    with current_app.open_resource("static/texts/origins.txt", mode="rb") as o:
        origin_values = o.read().decode("utf-8").splitlines()
    for i in range(0, origin_amount):
        origin = Origin(name=origin_values[random.randint(0, len(origin_values) - 1)])
        db.session.add(origin)
        created += 1
    db.session.commit()

    if item_amount == 0:
        item_amount = random.randint(50, 250)
    for i in range(0, item_amount):
        item = Item(type_id=random.randint(1, type_amount), location_id=random.randint(1, location_amount), origin_id=random.randint(1, origin_amount), name=f"Test {random.randint(1000, 9999)}", comment="Comment for longer texts", size=str(random.randint(5, 110)) + "cm")
        db.session.add(item)
        db.session.commit()
        src_path = os.path.join(current_app.root_path, rf"static\{current_app.config['MEDIA_ROOT_PATH']}\images/dummy\{random.randint(0, 63)}.png")
        dest_path = os.path.join(current_app.root_path, rf"static\{current_app.config['MEDIA_ROOT_PATH']}\images\{item.id}")
        dest_file = rf"{dest_path}\0.png"
        os.makedirs(dest_path, exist_ok=True)
        copyfile(src_path, dest_file)
        thumbnail = Image(path=f"{item.id}/0.png", is_thumbnail=True, item_id=item.id)
        db.session.add(thumbnail)
        created += 1
    db.session.commit()
    return created


def create_test_users(amount, password):
    if amount == 0:
        amount = random.randint(15, 100)
    for i in range(0, amount):
        role_number = random.randint(0, 10)
        if role_number < 5:
            role = Role.Visitor
        elif role_number < 8:
            role = Role.User
        else:
            role = Role.Editor
        create_account(f"Account_{random.randint(0, 2000000000)}", password, role)
    return amount


def backup(include_database=True, include_media=True, type="full"):
    fileobj = io.BytesIO()
    paths = []
    if include_database:
        paths.append((current_app.config.get("STORAGE_DATABASE_FILE"), os.path.join(current_app.root_path, current_app.config.get("STORAGE_DATABASE_FILE"))))
    media_dir = os.path.join(current_app.root_path, f"static/{current_app.config.get('MEDIA_ROOT_PATH')}/images/")
    image_objects = Image.query.all()
    if include_media:
        for image_object in image_objects:
            paths.append((image_object.path, media_dir + image_object.path))  # pragma: no cover
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
    response.headers.set("Content-Disposition", "attachment", filename=f"backup_{type}_{time_string}.zip")
    return response
