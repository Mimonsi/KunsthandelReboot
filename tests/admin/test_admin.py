import os
import unittest
from gettext import gettext

from kunsthandel import db, create_app, config
from kunsthandel.models import Role, User, Item, Type, Location, Origin
from tests import DatabaseTestCase


class TestStorageOverview(DatabaseTestCase):
    def setUp(self):
        app = create_app(config_class=config.TestConfig)
        app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///testing.db?charset=utf8mb4'
        app.config["STORAGE_DATABASE_FILE"] = 'testing.db'
        self.client = app.test_client()
        db.app = app
        db.drop_all()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        # TODO: Delete database file

    def test_permission_storage(self):
        """ Check permissions to access storage overview """
        pairs = {Role.External: 403, Role.Visitor: 403, Role.User: 403, Role.Editor: 403, Role.Administrator: 200}
        for role, status in pairs.items():
            with self.subTest(role=role.name):
                self._login_user(role=role, username=f"test_{role.name}")
                result = self.client.get("/admin/storage_overview")
                self.assertEqual(status, result.status_code)
                self._logout()

    def test_storage_overview(self):
        self._login_user(role=Role.Administrator, username="admin")
        result = self.client.get("/admin/storage_overview")
        self.assertEqual(200, result.status_code)
        self.assertIn(gettext('Storage Overview'), str(result.data))


class TestAdminPermission(DatabaseTestCase):
    def test_permission_home(self):
        """ Check permissions to access admin home """
        pairs = {Role.External: 403, Role.Visitor: 403, Role.User: 403, Role.Editor: 403, Role.Administrator: 200}
        for role, status in pairs.items():
            with self.subTest(role=role.name):
                self._login_user(role=role, username=f"test_{role.name}")
                result = self.client.get("/admin/")
                self.assertEqual(status, result.status_code)
                if role == Role.Administrator:
                    self.assertIn("Welcome, test_Administrator", str(result.data))
                self._logout()


class TestRoutes(DatabaseTestCase):
    def setUp(self):
        super().setUp()
        self._login_user(role=Role.Administrator, username="Administrator")

    def test_home_post(self):
        """ Post request to home should not be allowed """
        result = self.client.post("/admin/")
        self.assertEqual(405, result.status_code)

    def test_create_users_get(self):
        """ Get request should not be allowed """
        result = self.client.get("/admin/create_users")
        self.assertEqual(405, result.status_code)

    def test_create_users_successful(self):
        result = self.client.post("/admin/create_users", data=dict(
            account_amount=0,
            password="password",
            confirm_password="password",
        ), follow_redirects=True)
        self.assertGreater(len(User.query.all()), 1)  # More than 1 user account after bulk creation
        self.assertEqual("/admin/", result.request.path)
        self.assertIn("Successfully created", str(result.data))
        self.assertEqual(200, result.status_code)

    def test_create_users_passwords_unequal(self):
        result = self.client.post("/admin/create_users", data=dict(
            account_amount=0,
            password="password",
            confirm_password="other_password",
        ), follow_redirects=True)
        self.assertEqual(1, len(User.query.all()))  # More than 1 user account after bulk creation
        self.assertEqual("/admin/", result.request.path)
        self.assertIn("Field must be equal to password.", str(result.data))
        self.assertEqual(400, result.status_code)

    def test_create_items_get(self):
        """ Get request should not be allowed """
        result = self.client.get("/admin/create_items")
        self.assertEqual(405, result.status_code)

    def test_create_items_successful(self):
        result = self.client.post("/admin/create_items", data=dict(
            item_amount=0,
            type_amount=2,
            location_amount=2,
            origin_amount=2,
        ), follow_redirects=True)
        self.assertGreater(len(Item.query.all()), 1)  # More than 1 item after bulk creation
        self.assertEqual(2, len(Type.query.all()))  # Exactly 2 types, locations and origins after bulk creation
        self.assertEqual(2, len(Location.query.all()))
        self.assertEqual(2, len(Origin.query.all()))
        self.assertEqual("/admin/", result.request.path)
        self.assertIn("Successfully created", str(result.data))
        self.assertEqual(200, result.status_code)

    def test_create_items_amount_invalid(self):
        result = self.client.post("/admin/create_items", data=dict(
            item_amount=0,
            type_amount=2,
            location_amount=2,
            origin_amount="text",  # Text is not allowed here
        ), follow_redirects=True)
        self.assertEqual(0, len(Type.query.all()))  # Exactly 0 types, locations and origins after bulk creation
        self.assertEqual(0, len(Location.query.all()))
        self.assertEqual(0, len(Origin.query.all()))
        self.assertEqual(0, len(Item.query.all()))  # More than 1 user account after bulk creation
        self.assertEqual("/admin/", result.request.path)
        self.assertIn("This field is required.", str(result.data))
        self.assertEqual(400, result.status_code)


class TestQRCodeCreation(DatabaseTestCase):
    def setUp(self):
        super().setUp()
        self._login_user(role=Role.Administrator, username="Administrator")
        item = Item()
        db.session.add(item)
        db.session.commit()

    def test_create_qr_codes_get(self):
        """ Get request should not be allowed """
        result = self.client.get("/admin/qr_printsheet")
        self.assertEqual(405, result.status_code)

    def test_create_qr_codes_successful(self):
        result = self.client.post("/admin/qr_printsheet", data=dict(
            code_version=1,
            code_size=10,
            code_border_size=5,
        ), follow_redirects=True)
        self.assertEqual("/admin/qr_printsheet", result.request.path)
        self.assertIn("<img src", str(result.data))
        self.assertEqual(200, result.status_code)

    def test_create_qr_codes_amount_invalid(self):
        result = self.client.post("/admin/qr_printsheet", data=dict(
            code_version=1,
            code_size=10,
            code_border_size="text",  # Text is not allowed here
        ), follow_redirects=True)
        self.assertEqual("/admin/", result.request.path)
        self.assertIn("Something went wrong. This is awkward...", str(result.data))
        self.assertEqual(400, result.status_code)


class TestErrorHandlers(DatabaseTestCase):
    def test_403(self):
        self._login_user(role=Role.Administrator, username="admin")
        result = self.client.get("/admin/403", follow_redirects=True)
        self.assertEqual(403, result.status_code)
        self.assertIn("403", str(result.data))

    def test_404(self):
        self._login_user(role=Role.Administrator, username="admin")
        result = self.client.get("/admin/404", follow_redirects=True)
        self.assertEqual(404, result.status_code)
        self.assertIn("404", str(result.data))

    def test_500(self):
        self._login_user(role=Role.Administrator, username="admin")
        result = self.client.get("/admin/500", follow_redirects=True)
        self.assertEqual(500, result.status_code)
        self.assertIn("500", str(result.data))


if __name__ == '__main__':
    unittest.main()
