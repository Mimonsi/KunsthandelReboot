import os
import unittest
from gettext import gettext

from kunsthandel import db, create_app, config
from kunsthandel.models import Role
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
                self._login_user(role=role, username="test_" + str(role.name))
                result = self.client.get("/admin/storage_overview")
                self.assertEqual(result.status_code, status)
                self._logout()

    def test_storage_overview(self):
        self._login_user(role=Role.Administrator, username="admin")
        result = self.client.get("/admin/storage_overview")
        self.assertEqual(result.status_code, 200)
        self.assertIn(gettext('Storage Overview'), str(result.data))


class TestRoutes(DatabaseTestCase):
    def test_permission_home(self):
        """ Check permissions to access admin home """
        pairs = {Role.External: 403, Role.Visitor: 403, Role.User: 403, Role.Editor: 403, Role.Administrator: 200}
        for role, status in pairs.items():
            with self.subTest(role=role.name):
                self._login_user(role=role, username="test_" + str(role.name))
                result = self.client.get("/admin/")
                self.assertEqual(result.status_code, status)
                self.assertIn("Welcome, test_Administrator", str(result.data))
                self._logout()

    def test_home_post(self):
        """ Post request to home should not be allowed """
        self._login_user(role=Role.Administrator, username="Administrator")
        result = self.client.post("/admin/")
        self.assertEqual(result.status_code, 405)


class TestErrorHandlers(DatabaseTestCase):
    def test_403(self):
        self._login_user(role=Role.Administrator, username="admin")
        result = self.client.get("/admin/403", follow_redirects=True)
        self.assertEqual(result.status_code, 403)
        self.assertIn("403", str(result.data))

    def test_404(self):
        self._login_user(role=Role.Administrator, username="admin")
        result = self.client.get("/admin/404", follow_redirects=True)
        self.assertEqual(result.status_code, 404)
        self.assertIn("404", str(result.data))

    def test_500(self):
        self._login_user(role=Role.Administrator, username="admin")
        result = self.client.get("/admin/500", follow_redirects=True)
        self.assertEqual(result.status_code, 500)
        self.assertIn("500", str(result.data))


if __name__ == '__main__':
    unittest.main()
