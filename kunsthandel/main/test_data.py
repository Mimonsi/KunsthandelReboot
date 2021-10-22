import random

from kunsthandel import db
from kunsthandel.main import utils
from kunsthandel.models import User, create_account, Role, Location, Origin, Type, Item, Image


def create_test_items():

    location1 = Location(name="Kunsthandel Raum 1")
    location2 = Location(name="Kunsthandel Raum 3")
    location3 = Location(name="Frankreich")
    location4 = Location(name="Lager")
    db.session.add(location1)
    db.session.add(location2)
    db.session.add(location3)
    db.session.add(location4)

    origin1 = Origin(name="Mali")
    origin2 = Origin(name="Kongo")
    origin3 = Origin(name="Mali2")
    origin4 = Origin(name="Brasilien")
    db.session.add(origin1)
    db.session.add(origin2)
    db.session.add(origin3)
    db.session.add(origin4)

    type1 = Type(name="Maske")
    type2 = Type(name="Statue")
    type3 = Type(name="Other")
    db.session.add(type1)
    db.session.add(type2)
    db.session.add(type3)

    for i in range(0, random.randint(50, 250)):
        item = Item(type_id=random.randint(1, 3), location_id=random.randint(1, 4), origin_id=random.randint(1, 4), name="Testname", comment="Comment for longer texts", size="10cm")
        item.qr_hash = utils.get_qr_hash()
        db.session.add(item)
        db.session.commit()
        thumbnail = Image(path="dummy/" + str(random.randint(0, 63)) + ".png", is_thumbnail=True, item_id=item.id)
        db.session.add(thumbnail)
    db.session.commit()
    return i*2


def create_test_users():
    create_account("External", "External", Role.External)
    create_account("External2", "External2", Role.External)
    create_account("Visitor", "Visitor", Role.Visitor)
    create_account("User", "User", Role.User)
    create_account("Editor", "Editor", Role.Editor)
    create_account("Administrator", "Administrator", Role.Administrator)
    amount = 6
    for i in range(0, random.randint(15, 100)):
        role = Role.External
        role_number = random.randint(0, 10)
        if role_number < 5:
            role = Role.Visitor
        elif role_number < 8:
            role = Role.User
        else:
            role = Role.Editor
        create_account("Account_" + str(random.randint(0, 2000000000)), "password", role)
        amount += 1
    return amount