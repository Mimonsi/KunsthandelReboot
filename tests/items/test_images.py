import unittest

from flask import current_app
from werkzeug.datastructures import FileStorage

from kunsthandel import db
from tests import DatabaseTestCase

from kunsthandel.models import Role, Item, Image


class TestImagePermissions(DatabaseTestCase):

    def test_permission_image_details(self):
        """ Check roles for permission to view image details """
        pairs = {Role.External: 403, Role.Visitor: 403, Role.User: 200, Role.Editor: 200, Role.Administrator: 200}
        for role, status in pairs.items():
            with self.subTest(role.name):
                self._login_user(role, f"test_{role.name}")
                image = Image(path="test.png")
                db.session.add(image)
                db.session.commit()
                result = self.client.get(f"/images/{image.id}")
                self.assertEqual(status, result.status_code)
                self._logout()

    def test_permission_item_delete(self):
        """ Check roles for permission to delete item """
        pairs = {Role.External: 403, Role.Visitor: 403, Role.User: 403, Role.Editor: 200, Role.Administrator: 200}
        for role, status in pairs.items():
            with self.subTest(role.name):
                self._login_user(role, f"test_{role.name}")
                item = Item()
                image = Image(path="test.png", item=item)
                db.session.add(image)
                db.session.commit()
                result = self.client.post(f"/images/{image.id}/delete", follow_redirects=True)
                self.assertEqual(status, result.status_code)
                self._logout()


class TestInvalidMethods(DatabaseTestCase):
    def setUp(self):
        super(TestInvalidMethods, self).setUp()
        admin = self._login_user(Role.Administrator, username="Administrator")

    def test_image_details_post(self):
        result = self.client.post("/images/1", follow_redirects=True)
        self.assertEqual(405, result.status_code)

    def test_delete_image_get(self):
        result = self.client.get("/images/1/delete", follow_redirects=True)
        self.assertEqual(405, result.status_code)


class TestDeleteImage(DatabaseTestCase):
    def setUp(self):
        super(TestDeleteImage, self).setUp()
        item = Item()
        image = Image(item=item, path="test.png")
        db.session.add(image)
        db.session.commit()
        admin = self._login_user(Role.Administrator, username="Administrator")

    def test_delete(self):
        """ Delete image """
        result = self.client.post(f"/images/1/delete", follow_redirects=True)
        self.assertEqual(200, result.status_code)
        self.assertEqual("/items/1/edit", result.request.path)  # Check redirect to owning item
        self.assertEqual(0, len(Item.query.get(1).images))


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
