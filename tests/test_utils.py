import unittest

from werkzeug.datastructures import FileStorage

from kunsthandel import create_app, config, db
from kunsthandel.models import Role
from tests import DatabaseTestCase


class TestRoleRequiredDecorator(DatabaseTestCase):

    def test_exempt_method(self):  # TODO not working correctly
        """ options method is exempt """
        self._login_user(role=Role.External)
        result = self.client.options(f"/admin/")
        self.assertEqual(200, result.status_code)

    def test_unauthorized(self):
        """ user is not logged in """
        result = self.client.get(f"/admin/", follow_redirects=True)
        self.assertEqual(200, result.status_code)
        self.assertEqual("/login", result.request.path)

    def test_forbidden(self):
        """ user has no permission to access function """
        self._login_user(role=Role.External)
        result = self.client.get(f"/admin/")
        self.assertEqual(403, result.status_code)


class TestRoleRequiredDecoratorExemptMethod(DatabaseTestCase):

    def setUp(self):
        app = create_app(config_class=config.TestConfig)
        self.client = app.test_client()
        db.app = app
        app.config["LOGIN_DISABLED"] = True
        db.drop_all()
        db.create_all()

    def test_forbidden(self):
        """ login is disabled, user can continue without login """
        result = self.client.get(f"/admin/")
        self.assertEqual(200, result.status_code)
        self.assertEqual("/admin/", result.request.path)


#class TestImageUpload(DatabaseTestCase):
    #def test_thumbnail_upload(self):
        #self._login_user(role=Role.Administrator)
        #FileStorage()


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
