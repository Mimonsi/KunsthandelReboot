import unittest

from kunsthandel import create_app, config, db
from kunsthandel.models import Role, User, create_account


class TestRoutes(unittest.TestCase):

    def setUp(self):
        app = create_app(config_class=config.TestConfig)
        self.client = app.test_client()
        db.app = app
        db.drop_all()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_login_redirect(self):
        """ Test if any route redirects to login """
        result = self.client.get('/home')
        assert result.status_code == 302
        assert "/login" in result.headers["Location"]

    def _insert_user(self, username, password, role=Role.External):
        create_account(username=username, password=password, role=role)

    def test_successful_login(self):
        """ Test if login form works correctly """
        self._insert_user("test", "password", Role.Administrator)
        result = self.client.post("/login", data=dict(
            username="test",
            password="password"
        ), follow_redirects=True)
        self.assertEqual(result.status_code, 200)
        self.assertIn("Login successful", str(result.data))

    def test_failed_login(self):
        """ Test if login form works correctly """
        self._insert_user("test", "password", Role.Administrator)
        result = self.client.post("/login", data=dict(
            username="test",
            password="wrongpassword"
        ), follow_redirects=True)
        self.assertEqual(result.status_code, 401)
        self.assertIn("Login unsuccessful", str(result.data))

    def test_unvalidated_login(self):
        """ Test if login form works correctly """
        self._insert_user("test", "password", Role.Administrator)
        result = self.client.post("/login", data=dict(
            username="test"
        ), follow_redirects=True)
        self.assertEqual(result.status_code, 400)
        self.assertIn("This field is required.", str(result.data))


if __name__ == '__main__':
    unittest.main()
