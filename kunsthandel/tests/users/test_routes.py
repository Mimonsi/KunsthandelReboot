import unittest

from flask_login import login_user

from kunsthandel import create_app, config, db
from kunsthandel.models import Role, User, create_account


class TestLoginLogout(unittest.TestCase):

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
        self.assertEqual(result.status_code, 302)
        self.assertIn("/login", result.headers["Location"])

    def _insert_user(self, username, password, role=Role.External):
        return create_account(username=username, password=password, role=role)

    def _login_user(self, role=Role.External):
        self._insert_user("test", "password", role=role)
        result = self.client.post("/login", data=dict(
            username="test",
            password="password"
        ), follow_redirects=True)
        return result

    def test_successful_login(self):
        """ Login with correct data """
        self._insert_user("test", "password", Role.Administrator)
        result = self.client.post("/login", data=dict(
            username="test",
            password="password"
        ), follow_redirects=True)
        self.assertEqual(result.status_code, 200)
        self.assertIn("Login successful", str(result.data))

    def test_failed_login(self):
        """ Login with wrong password """
        self._insert_user("test", "password", Role.Administrator)
        result = self.client.post("/login", data=dict(
            username="test",
            password="wrongpassword"
        ), follow_redirects=True)
        self.assertEqual(result.status_code, 401)
        self.assertIn("Login unsuccessful", str(result.data))

    def test_unvalidated_login(self):
        """ Login with missing password """
        self._insert_user("test", "password", Role.Administrator)
        result = self.client.post("/login", data=dict(
            username="test"
        ), follow_redirects=True)
        self.assertEqual(result.status_code, 400)
        self.assertIn("This field is required.", str(result.data))

    def test_logout_not_logged_in(self):
        """ Logout works when not logged in """
        result = self.client.get("/logout")
        self.assertEqual(result.status_code, 302)  # Should redirect to login
        self.assertIn("/login", result.headers["Location"])

    def test_logout(self):
        """ Logout works when logged in """
        self._login_user(Role.External)
        result = self.client.get("/logout")
        self.assertEqual(result.status_code, 302)  # Should redirect to login
        self.assertIn("/login", result.headers["Location"])


class TestUserPermissions(unittest.TestCase):
    def setUp(self):
        app = create_app(config_class=config.TestConfig)
        self.client = app.test_client()
        db.app = app
        db.drop_all()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def _login_user(self, role=Role.External, username="test"):
        user = create_account(username, "password", role=role)
        result = self.client.post("/login", data=dict(
            username=username,
            password="password"
        ), follow_redirects=True)
        return user

    def _logout(self):
        self.client.get("/logout")

    def test_permission_edit_own_user(self):
        """ Check roles for permission to edit own profile """
        pairs = {Role.External: 403, Role.Visitor: 403, Role.User: 200, Role.Editor: 200, Role.Administrator: 200}
        for role, status in pairs.items():
            with self.subTest(role=role.name):
                self._login_user(role=role, username="test_" + str(role.name))
                result = self.client.get("/users/me")
                self.assertEqual(result.status_code, status)
                self._logout()

    def test_permission_edit_user(self):
        """ Check roles for permission to edit user profiles """
        pairs = {Role.External: 403, Role.Visitor: 403, Role.User: 403, Role.Editor: 403, Role.Administrator: 200}
        for role, status in pairs.items():
            with self.subTest(role=role.name):
                user = self._login_user(role=role, username="test_" + str(role.name))
                result = self.client.get("/users/" + str(user.id) + "")
                self.assertEqual(result.status_code, status)
                self._logout()

    def test_permission_create_user(self):
        """ Check roles for permission to create user profiles """
        pairs = {Role.External: 403, Role.Visitor: 403, Role.User: 403, Role.Editor: 403, Role.Administrator: 200}
        for role, status in pairs.items():
            with self.subTest(role=role.name):
                self._login_user(role=role, username="test_" + str(role.name))
                result = self.client.get("/users/create")
                self.assertEqual(result.status_code, status)
                self._logout()

    def test_permission_delete_user(self):
        """ Check roles for permission to delete user profiles """
        pairs = {Role.External: 403, Role.Visitor: 403, Role.User: 403, Role.Editor: 403, Role.Administrator: 302}
        for role, status in pairs.items():
            with self.subTest(role=role.name):
                user = self._login_user(role=role, username="test_" + str(role.name))
                result = self.client.post("/users/" + str(user.id) + "/delete")
                self.assertEqual(result.status_code, status)
                self._logout()

    def test_permission_users(self):
        """ Check roles for permission to view users overview """
        pairs = {Role.External: 403, Role.Visitor: 403, Role.User: 403, Role.Editor: 403, Role.Administrator: 200}
        for role, status in pairs.items():
            with self.subTest(role=role.name):
                user = self._login_user(role=role, username="test_" + str(role.name))
                result = self.client.get("/users")
                self.assertEqual(result.status_code, status)
                self._logout()

    def test_create_user_successful(self):
        """ Create new user account by an Administrator """
        admin = self._login_user(Role.Administrator, username="Administrator")
        result = self.client.post("/users/create", data=dict(
            username="test",
            password="password",
            confirm_password="password",
            role=2,
            locale="en"
        ), follow_redirects=True)

        self.assertIn("/users", result.request.url)
        self.assertEqual(result.status_code, 200)
        created_user = User.query.filter_by(username="test").first()
        self.assertIsNotNone(created_user, "User now exists in database")


if __name__ == '__main__':
    unittest.main()
