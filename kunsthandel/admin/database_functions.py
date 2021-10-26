import random

from kunsthandel import db
from kunsthandel.main import utils
from kunsthandel.models import User, create_account, Role, Location, Origin, Type, Item, Image


def create_test_items(item_amount, type_amount, location_amount, origin_amount):

    type_values = []
    location_values = []
    origin_values = []
    created = 0
    with open('kunsthandel/static/texts/types.txt', mode="r", encoding="utf-8") as t:
        type_values = t.read().splitlines()
    for i in range(0, type_amount):
        type = Type(name=type_values[random.randint(0, len(type_values)-1)])
        db.session.add(type)
        created += 1
    with open('kunsthandel/static/texts/locations.txt', mode="r", encoding="utf-8") as l:
        location_values = l.read().splitlines()
    for i in range(0, location_amount):
        location = Location(name=location_values[random.randint(0, len(location_values)-1)])
        db.session.add(location)
        created += 1
    with open('kunsthandel/static/texts/origins.txt', mode="r", encoding="utf-8") as o:
        origin_values = o.read().splitlines()
    for i in range(0, origin_amount):
        origin = Origin(name=origin_values[random.randint(0, len(origin_values)-1)])
        db.session.add(origin)
        created += 1
    db.session.commit()

    if item_amount == 0:
        item_amount = random.randint(50, 250)
    for i in range(0, item_amount):
        item = Item(type_id=random.randint(1, type_amount), location_id=random.randint(1, location_amount), origin_id=random.randint(1, origin_amount), name="Test " + str(random.randint(1000, 9999)), comment="Comment for longer texts", size=str(random.randint(5, 110)) + "cm")
        item.qr_hash = utils.get_qr_hash()
        db.session.add(item)
        db.session.commit()
        thumbnail = Image(path="dummy/" + str(random.randint(0, 63)) + ".png", is_thumbnail=True, item_id=item.id)
        db.session.add(thumbnail)
        created += 1
    db.session.commit()
    return created


def create_test_users(amount, password):
    if amount == 0:
        amount = random.randint(15, 100)
    for i in range(0, amount):
        role = Role.External
        role_number = random.randint(0, 10)
        if role_number < 5:
            role = Role.Visitor
        elif role_number < 8:
            role = Role.User
        else:
            role = Role.Editor

        create_account("Account_" + str(random.randint(0, 2000000000)), password, role)
        amount += 1
    return amount