import unittest

from flask import current_app
from werkzeug.datastructures import FileStorage

from kunsthandel import db
from tests import DatabaseTestCase

from kunsthandel.models import Role, Item


class TestItemPermissions(DatabaseTestCase):

    def test_permission_token(self):
        """ Check roles for permission to access item token """
        pairs = {Role.External: 200, Role.Visitor: 200, Role.User: 200, Role.Editor: 200, Role.Administrator: 200}
        for role, status in pairs.items():
            with self.subTest(role=role.name):
                self._login_user(role=role, username=f"test_{role.name}")
                item = Item()
                db.session.add(item)
                db.session.commit()
                result = self.client.get(f"/code/{item.qr_hash}")
                self.assertEqual(status, result.status_code)
                self._logout()

    def test_permission_items(self):
        """ Check roles for permission to view items overview """
        pairs = {Role.External: 403, Role.Visitor: 403, Role.User: 200, Role.Editor: 200, Role.Administrator: 200}
        for role, status in pairs.items():
            with self.subTest(role=role.name):
                self._login_user(role=role, username=f"test_{role.name}")
                result = self.client.get("/items")
                self.assertEqual(status, result.status_code)
                self._logout()

    def test_permission_item_details(self):
        """ Check roles for permission to view item details """
        pairs = {Role.External: 403, Role.Visitor: 403, Role.User: 200, Role.Editor: 200, Role.Administrator: 200}
        for role, status in pairs.items():
            with self.subTest(role=role.name):
                self._login_user(role=role, username=f"test_{role.name}")
                item = Item()
                db.session.add(item)
                db.session.commit()
                result = self.client.get(f"/items/{item.id}")
                self.assertEqual(status, result.status_code)
                self._logout()

    def test_permission_item_edit(self):
        """ Check roles for permission to view item edit route """
        pairs = {Role.External: 403, Role.Visitor: 403, Role.User: 403, Role.Editor: 200, Role.Administrator: 200}
        for role, status in pairs.items():
            with self.subTest(role=role.name):
                self._login_user(role=role, username=f"test_{role.name}")
                item = Item()
                db.session.add(item)
                db.session.commit()
                result = self.client.get(f"/items/{item.id}/edit")
                self.assertEqual(status, result.status_code)
                self._logout()

    def test_permission_item_delete(self):
        """ Check roles for permission to delete item """
        pairs = {Role.External: 403, Role.Visitor: 403, Role.User: 403, Role.Editor: 200, Role.Administrator: 200}
        for role, status in pairs.items():
            with self.subTest(role=role.name):
                self._login_user(role=role, username=f"test_{role.name}")
                item = Item()
                db.session.add(item)
                db.session.commit()
                result = self.client.post(f"/items/{item.id}/delete")
                self.assertEqual(status, result.status_code)
                self._logout()


class TestCreateItem(DatabaseTestCase):
    def setUp(self):
        super(TestCreateItem, self).setUp()
        admin = self._login_user(Role.Administrator, username="Administrator")

    def test_create_item_successful(self):
        """ Create new item by an Administrator """
        result = self.client.post("/items/create", data=dict(
            name="TestItem",
        ), follow_redirects=True)

        self.assertEqual("/items", result.request.path)
        self.assertEqual(200, result.status_code)
        created_item = Item.query.first()
        self.assertIsNotNone(created_item, "Item now exists in database")

    def test_create_item_with_thumbnail(self):
        """ Create new item with thumbnail """
        with db.app.app_context():
            with current_app.open_resource("static/tests/test.png", mode="rb") as fp:
                thumbnail = FileStorage(fp)
                result = self.client.post("/items/create", data=dict(
                    name="TestItem",
                    thumbnail=thumbnail
                ), follow_redirects=True)
        self.assertEqual("/items", result.request.path)
        self.assertEqual(200, result.status_code)
        created_item = Item.query.first()
        self.assertIsNotNone(created_item.thumbnail())
        self.assertIsNotNone(created_item, "Item now exists in database")

    def test_create_item_with_images(self):
        """ Create new item with images """
        with db.app.app_context(), current_app.open_resource("static/tests/test.png", mode="rb") as fp1, current_app.open_resource("static/tests/test.png", mode="rb") as fp2:
            image_1 = FileStorage(fp1)
            image_2 = FileStorage(fp2)
            result = self.client.post("/items/create", data=dict(
                name="TestItem",
                images=[image_1, image_2]
            ), follow_redirects=True)
        self.assertEqual("/items", result.request.path)
        self.assertEqual(200, result.status_code)
        created_item = Item.query.first()
        self.assertIsNotNone(created_item.images)
        self.assertEqual(2, len(created_item.images))
        self.assertIsNotNone(created_item, "Item now exists in database")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
