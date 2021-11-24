import unittest

from kunsthandel import db
from kunsthandel.main.utils import get_qr_hash
from kunsthandel.models import User, Role, Location, Origin, Type, Image, Item
from tests import DatabaseTestCase


class TestDatabaseModels(DatabaseTestCase):
    def test_user_model(self):
        user = User(username="username", password="password", role_id=Role.Administrator.value)
        db.session.add(user)
        db.session.commit()
        self.assertIsNotNone(User.query.get(user.id))
        self.assertEqual("<User> (username=username, role_id=4)", str(user))
        self.assertEqual("Administrator", user.role())
        self.assertEqual(True, user.has_permission(3))
        self.assertEqual(False, user.has_permission(5))
        print(user)

    def test_location_model(self):
        location = Location(name="location")
        db.session.add(location)
        db.session.commit()
        self.assertIsNotNone(Location.query.get(location.id))
        self.assertEqual(f"<Location> (id={location.id}, name=location)", str(location))
        self.assertEqual("Location", location.model_name())
        print(location)

    def test_origin_model(self):
        origin = Origin(name="origin")
        db.session.add(origin)
        db.session.commit()
        self.assertIsNotNone(Origin.query.get(origin.id))
        self.assertEqual(f"<Origin> (id={origin.id}, name=origin)", str(origin))
        self.assertEqual( "Origin", origin.model_name())
        print(origin)

    def test_type_model(self):
        type = Type(name="type")
        db.session.add(type)
        db.session.commit()
        self.assertIsNotNone(Type.query.get(type.id))
        self.assertEqual(f"<Type> (id={type.id}, name=type)", str(type))
        self.assertEqual("Type", type.model_name())
        print(type)

    def test_image_model(self):
        image = Image(path="test.png")
        db.session.add(image)
        db.session.commit()
        self.assertIsNotNone(Image.query.get(image.id))
        self.assertEqual( f"<Image> (id={image.id}, path=test.png, item_id=None, is_thumbnail=False)", str(image))
        #self.assertEqual(image.url(), "") This is not testable, as URL_FOR requires application context
        print(image)

    def test_item_model(self):
        item = Item(qr_hash=get_qr_hash())
        db.session.add(item)
        db.session.commit()
        self.assertIsNotNone(Item.query.get(item.id))
        self.assertEqual(f"<Item> (id={item.id}, name=None, type=None, location=None, origin=None)", str(item))
        self.assertEqual(None, item.thumbnail())
        print(item)


if __name__ == '__main__':
    unittest.main()
