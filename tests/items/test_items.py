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
            with self.subTest(role.name):
                self._login_user(role, f"test_{role.name}")
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
            with self.subTest(role.name):
                self._login_user(role, f"test_{role.name}")
                result = self.client.get("/items")
                self.assertEqual(status, result.status_code)
                self._logout()

    def test_permission_item_details(self):
        """ Check roles for permission to view item details """
        pairs = {Role.External: 403, Role.Visitor: 403, Role.User: 200, Role.Editor: 200, Role.Administrator: 200}
        for role, status in pairs.items():
            with self.subTest(role.name):
                self._login_user(role, f"test_{role.name}")
                item = Item()
                db.session.add(item)
                db.session.commit()
                result = self.client.get(f"/items/{item.id}")
                self.assertEqual(status, result.status_code)
                self._logout()

    def test_permission_item_create(self):
        """ Check roles for permission to view item create route """
        pairs = {Role.External: 403, Role.Visitor: 403, Role.User: 403, Role.Editor: 200, Role.Administrator: 200}
        for role, status in pairs.items():
            with self.subTest(role.name):
                self._login_user(role, f"test_{role.name}")
                result = self.client.get(f"/items/create")
                self.assertEqual(status, result.status_code)
                self._logout()

    def test_permission_item_edit(self):
        """ Check roles for permission to view item edit route """
        pairs = {Role.External: 403, Role.Visitor: 403, Role.User: 403, Role.Editor: 200, Role.Administrator: 200}
        for role, status in pairs.items():
            with self.subTest(role.name):
                self._login_user(role, f"test_{role.name}")
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
            with self.subTest(role.name):
                self._login_user(role, f"test_{role.name}")
                item = Item()
                db.session.add(item)
                db.session.commit()
                result = self.client.post(f"/items/{item.id}/delete", follow_redirects=True)
                self.assertEqual(status, result.status_code)
                self._logout()

    def test_permission_item_code(self):
        """ Check roles for permission to create item code """
        pairs = {Role.External: 403, Role.Visitor: 403, Role.User: 200, Role.Editor: 200, Role.Administrator: 200}
        for role, status in pairs.items():
            with self.subTest(role.name):
                self._login_user(role, f"test_{role.name}")
                item = Item()
                db.session.add(item)
                db.session.commit()
                result = self.client.get(f"/items/{item.id}/code", follow_redirects=True)
                self.assertEqual(status, result.status_code)
                self._logout()


class TestInvalidMethods(DatabaseTestCase):
    def setUp(self):
        super(TestInvalidMethods, self).setUp()
        admin = self._login_user(Role.Administrator, username="Administrator")

    def test_item_token_post(self):
        result = self.client.post("/code/x", follow_redirects=True)
        self.assertEqual(405, result.status_code)

    def test_items_post(self):
        result = self.client.post("/items", follow_redirects=True)
        self.assertEqual(405, result.status_code)

    def test_item_details_post(self):
        result = self.client.post("/items/1", follow_redirects=True)
        self.assertEqual(405, result.status_code)

    def test_delete_item_get(self):
        result = self.client.get("/items/1/delete", follow_redirects=True)
        self.assertEqual(405, result.status_code)

    def test_delete_image_get(self):
        result = self.client.get("/items/1/images/1/delete", follow_redirects=True)
        self.assertEqual(405, result.status_code)

    def test_item_code(self):
        result = self.client.post("/items/1/code", follow_redirects=True)
        self.assertEqual(405, result.status_code)


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
        with db.app.app_context(), current_app.open_resource("static/tests/test.png", mode="rb") as fp:
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
        with db.app.app_context(), current_app.open_resource("static/tests/test.png",
                                                             mode="rb") as fp1, current_app.open_resource(
            "static/tests/test.png", mode="rb") as fp2:
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

    def test_create_item_with_empty_images(self):
        """ Create new item with empty image list """
        with db.app.app_context():
            result = self.client.post("/items/create", data=dict(
                name="TestItem",
                images=[]
            ), follow_redirects=True)
        self.assertEqual("/items", result.request.path)
        self.assertEqual(200, result.status_code)
        created_item = Item.query.first()
        self.assertIsNotNone(created_item.images)
        self.assertEqual(0, len(created_item.images))
        self.assertIsNotNone(created_item, "Item now exists in database")

    def test_create_item_invalid_type(self):
        """ Create new item with empty image list """
        with db.app.app_context():
            result = self.client.post("/items/create", data=dict(
                name="TestItem",
                type=-1,
            ), follow_redirects=True)
        self.assertEqual("/items/create", result.request.path)
        self.assertEqual(400, result.status_code)
        created_item = Item.query.first()
        self.assertIsNone(created_item, "Item not created")


class TestEditItem(DatabaseTestCase):
    def setUp(self):
        super(TestEditItem, self).setUp()
        item = Item(name="testItem")
        db.session.add(item)
        db.session.commit()
        admin = self._login_user(Role.Administrator, username="Administrator")

    def test_edit_item_successful(self):
        """ Edit item by administrator """
        result = self.client.post(f"/items/1/edit", data=dict(
            name="afterEdit",
        ), follow_redirects=True)

        self.assertEqual("/items", result.request.path)
        self.assertEqual(200, result.status_code)
        beforeItem = Item.query.filter_by(name="testItem").first()
        afterItem = Item.query.filter_by(name="afterEdit").first()
        self.assertIsNone(beforeItem, "Item with before name does not exist anymore")
        self.assertIsNotNone(afterItem, "Item with changed name now exists in database")

    def test_edit_item_not_existing(self):
        """ Try editing non existing item """
        result = self.client.post(f"/items/2/edit", data=dict(
            name="afterEdit",
        ), follow_redirects=True)

        self.assertEqual("/items/2/edit", result.request.path)
        self.assertEqual(404, result.status_code)

    def test_edit_item_with_thumbnail(self):
        """ edit item with thumbnail """
        #  Also test thumbnail replacement logic
        for i in range(0, 2):
            with db.app.app_context(), current_app.open_resource("static/tests/test.png", mode="rb") as fp:
                thumbnail = FileStorage(fp)
                result = self.client.post("/items/1/edit", data=dict(
                    name="afterEdit",
                    thumbnail=thumbnail
                ), follow_redirects=True)
            self.assertEqual("/items", result.request.path)
            self.assertEqual(200, result.status_code)
            updated_item = Item.query.get(1)
            self.assertIsNotNone(updated_item.thumbnail())
            self.assertIsNotNone(updated_item, "Item still exists in database")

    def test_edit_item_with_images(self):
        """ Create new item with images """
        with db.app.app_context(), current_app.open_resource("static/tests/test.png",
                                                             mode="rb") as fp1, current_app.open_resource(
            "static/tests/test.png", mode="rb") as fp2:
            image_1 = FileStorage(fp1)
            image_2 = FileStorage(fp2)
            result = self.client.post("/items/1/edit", data=dict(
                name="afterEdit",
                images=[image_1, image_2]
            ), follow_redirects=True)
        self.assertEqual("/items", result.request.path)
        self.assertEqual(200, result.status_code)
        created_item = Item.query.first()
        self.assertIsNotNone(created_item.images)
        self.assertEqual(2, len(created_item.images))
        self.assertIsNotNone(created_item, "Item still exists in database")

    def test_edit_item_with_empty_images(self):
        """ Create new item with empty image list """
        with db.app.app_context():
            result = self.client.post("/items/1/edit", data=dict(
                name="afterEdit",
                images=[]
            ), follow_redirects=True)
        self.assertEqual("/items", result.request.path)
        self.assertEqual(200, result.status_code)
        created_item = Item.query.first()
        self.assertIsNotNone(created_item.images)
        self.assertEqual(0, len(created_item.images))
        self.assertIsNotNone(created_item, "Item still exists in database")

    def test_edit_item_invalid_type(self):
        """ Create new item with empty image list """
        with db.app.app_context():
            result = self.client.post("/items/1/edit", data=dict(
                name="afterRename",
                type=-1,
            ), follow_redirects=True)
        self.assertEqual("/items/1/edit", result.request.path)
        self.assertEqual(400, result.status_code)
        unedited_item = Item.query.get(1)
        self.assertEqual("testItem", unedited_item.name)

    def test_edit_item_delete_image(self):
        """ Delete images of item """
        with db.app.app_context(), current_app.open_resource("static/tests/test.png",
                                                             mode="rb") as fp1:
            image_1 = FileStorage(fp1)
            result = self.client.post("/items/1/edit", data=dict(
                name="afterEdit",
                images=[image_1]
            ), follow_redirects=True)
        self.assertEqual("/items", result.request.path)
        self.assertEqual(200, result.status_code)
        editedItem = Item.query.get(1)
        self.assertIsNotNone(editedItem.images)
        self.assertEqual(1, len(editedItem.images))
        image = Item.query.get(1).images[0]
        result = self.client.post(f"/items/{editedItem.id}/images/{image.id}/delete", follow_redirects=True)
        self.assertEqual(200, result.status_code)
        self.assertEqual(0, len(Item.query.get(1).images))


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
