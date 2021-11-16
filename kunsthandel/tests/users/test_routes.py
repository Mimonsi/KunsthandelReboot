import unittest

from flask_login import login_user

from kunsthandel import create_app, config, db
from kunsthandel.models import Role, User, create_account


def _login_user(self, role=Role.External, username="test"):
    user = create_account(username, "password", role=role)
    result = self.client.post("/login", data=dict(
        username=username,
        password="password"
    ), follow_redirects=True)
    return user


def _insert_user(self, username, password, role=Role.External):
    return create_account(username=username, password=password, role=role)


def _logout(self):
    self.client.get("/logout")


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

    def test_login_page(self):
        """ Show Login Page """
        result = self.client.get("/login")
        self.assertEqual(result.status_code, 200)

    def test_login_page_logged_in(self):
        """ Test redirect to home page as logged in user """
        _login_user(self, Role.User)
        result = self.client.get("/login")
        self.assertEqual(result.status_code, 302)
        self.assertIn("/home", result.headers["Location"])

    def test_successful_login(self):
        """ Login with correct data """
        _insert_user(self, "test", "password", Role.Administrator)
        result = self.client.post("/login", data=dict(
            username="test",
            password="password"
        ), follow_redirects=True)
        self.assertEqual(result.status_code, 200)
        self.assertIn("Login successful", str(result.data))

    def test_failed_login(self):
        """ Login with wrong password """
        _insert_user(self, "test", "password", Role.Administrator)
        result = self.client.post("/login", data=dict(
            username="test",
            password="wrongpassword"
        ), follow_redirects=True)
        self.assertEqual(result.status_code, 401)
        self.assertIn("Login unsuccessful", str(result.data))

    def test_unvalidated_login(self):
        """ Login with missing password """
        _insert_user(self, "test", "password", Role.Administrator)
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
        _login_user(self, Role.External)
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

    def test_permission_edit_own_user(self):
        """ Check roles for permission to edit own profile """
        pairs = {Role.External: 403, Role.Visitor: 403, Role.User: 200, Role.Editor: 200, Role.Administrator: 200}
        for role, status in pairs.items():
            with self.subTest(role=role.name):
                _login_user(self, role=role, username="test_" + str(role.name))
                result = self.client.get("/users/me")
                self.assertEqual(result.status_code, status)
                _logout(self)

    def test_permission_edit_user(self):
        """ Check roles for permission to edit user profiles """
        pairs = {Role.External: 403, Role.Visitor: 403, Role.User: 403, Role.Editor: 403, Role.Administrator: 200}
        for role, status in pairs.items():
            with self.subTest(role=role.name):
                user = _login_user(self, role=role, username="test_" + str(role.name))
                result = self.client.get("/users/" + str(user.id) + "")
                self.assertEqual(result.status_code, status)
                _logout(self)

    def test_permission_create_user(self):
        """ Check roles for permission to create user profiles """
        pairs = {Role.External: 403, Role.Visitor: 403, Role.User: 403, Role.Editor: 403, Role.Administrator: 200}
        for role, status in pairs.items():
            with self.subTest(role=role.name):
                _login_user(self, role=role, username="test_" + str(role.name))
                result = self.client.get("/users/create")
                self.assertEqual(result.status_code, status)
                _logout(self)

    def test_permission_delete_user(self):
        """ Check roles for permission to delete user profiles """
        pairs = {Role.External: 403, Role.Visitor: 403, Role.User: 403, Role.Editor: 403, Role.Administrator: 302}
        for role, status in pairs.items():
            with self.subTest(role=role.name):
                user = _login_user(self, role=role, username="test_" + str(role.name))
                result = self.client.post("/users/" + str(user.id) + "/delete")
                self.assertEqual(result.status_code, status)
                _logout(self)

    def test_permission_users(self):
        """ Check roles for permission to view users overview """
        pairs = {Role.External: 403, Role.Visitor: 403, Role.User: 403, Role.Editor: 403, Role.Administrator: 200}
        for role, status in pairs.items():
            with self.subTest(role=role.name):
                user = _login_user(self, role=role, username="test_" + str(role.name))
                result = self.client.get("/users")
                self.assertEqual(result.status_code, status)
                _logout(self)


class TestCreateUser(unittest.TestCase):

    def setUp(self):
        app = create_app(config_class=config.TestConfig)
        self.client = app.test_client()
        db.app = app
        db.drop_all()
        db.create_all()
        admin = _login_user(self, Role.Administrator, username="Administrator")

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_create_user_successful(self):
        """ Create new user account by an Administrator """
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

    def test_create_user_successful_multiple(self):
        """ Create new user account by an Administrator with redirect to same form """
        result = self.client.post("/users/create?multiple=True", data=dict(
            username="test",
            password="password",
            confirm_password="password",
            role=2,
            locale="en"
        ), follow_redirects=True)
        self.assertIn("/users/create", result.request.url)  # Not optimal, /users is also in /users/create
        self.assertEqual(result.status_code, 200)
        created_user = User.query.filter_by(username="test").first()
        self.assertIsNotNone(created_user, "User now exists in database")

    def test_create_user_missing_parameter(self):
        """ Missing locale parameter """
        result = self.client.post("/users/create", data=dict(
            username="test",
            password="password",
            confirm_password="password",
            role=2,
        ), follow_redirects=True)

        self.assertIn("/users", result.request.url)
        self.assertEqual(result.status_code, 400)
        created_user = User.query.filter_by(username="test").first()
        self.assertIsNone(created_user, "User does not exists in database, as creation failed")

    def test_create_user_username_already_taken(self):
        """ Create account with taken username """
        result = self.client.post("/users/create", data=dict(
            username="Administrator",  # Same name as above
            password="password",
            confirm_password="password",
            role=2,
            locale="en"
        ), follow_redirects=True)
        self.assertIn("/users", result.request.url)
        self.assertEqual(result.status_code, 400)

    def test_create_user_passwords_unequal(self):
        """ Passwords don't match """
        result = self.client.post("/users/create", data=dict(
            username="test",
            password="password",
            confirm_password="other_password",
            role=2,
            locale="en"
        ), follow_redirects=True)

        self.assertIn("/users", result.request.url)
        self.assertEqual(result.status_code, 400)
        created_user = User.query.filter_by(username="test").first()
        self.assertIsNone(created_user, "User does not exists in database, as creation failed")


class TestEditOwnUser(unittest.TestCase):

    def setUp(self):
        app = create_app(config_class=config.TestConfig)
        self.client = app.test_client()
        db.app = app
        db.drop_all()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_edit_own_user_successful(self):
        """ Edit own locale by user """
        _login_user(self, role=Role.User, username="user")
        result = self.client.post("/users/me", data=dict(
            password="new_password",
            confirm_password="new_password",
            locale="de"
        ), follow_redirects=True)

        self.assertIn("/users/me", result.request.url)
        self.assertEqual(result.status_code, 200)
        user = User.query.filter_by(username="user").first()
        self.assertEqual(user.locale, "de", "User locale has been updated")

    def test_edit_own_user_missing_parameter(self):
        """ Missing parameter on own editing """
        _login_user(self, role=Role.User, username="user")
        result = self.client.post("/users/me", data=dict(
            password="new_password",
            confirm_password="new_password"
        ), follow_redirects=True)

        self.assertIn("/users/me", result.request.url)
        self.assertEqual(result.status_code, 400)
        user = User.query.filter_by(username="user").first()
        self.assertEqual(user.locale, "en", "User locale has not been updated")

    def test_edit_own_user_passwords_unequal(self):
        """ not matching passwords on editing own user """
        _login_user(self, role=Role.User, username="user")
        result = self.client.post("/users/me", data=dict(
            password="new_password",
            confirm_password="other_password",
            locale="de"
        ), follow_redirects=True)

        self.assertIn("/users/me", result.request.url)
        self.assertEqual(result.status_code, 400)
        user = User.query.filter_by(username="user").first()
        self.assertEqual(user.locale, "en", "User locale has not been updated")


class TestEditUser(unittest.TestCase):

    def setUp(self):
        app = create_app(config_class=config.TestConfig)
        self.client = app.test_client()
        db.app = app
        db.drop_all()
        db.create_all()
        admin = _login_user(self, Role.Administrator, username="Administrator")
        user = _insert_user(self, username="pre_change", password="password", role=Role.User)

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_edit_user_successful(self):
        """ Edit username by an Administrator """
        user = User.query.filter_by(username="pre_change").first()
        result = self.client.post("/users/" + str(user.id), data=dict(
            username="post_change",
            password="password",
            confirm_password="password",
            role=2,
            locale="en"
        ), follow_redirects=True)

        self.assertIn("/users", result.request.url)
        self.assertEqual(result.status_code, 200)
        old_user = User.query.filter_by(username="pre_change").first()
        updated_user = User.query.filter_by(username="post_change").first()
        self.assertIsNone(old_user, "User with previous name doesn't exists in database")
        self.assertIsNotNone(updated_user, "User with changed name exists in database")

    def test_edit_user_missing_parameter(self):
        """ Missing locale parameter """
        user = User.query.filter_by(username="pre_change").first()
        result = self.client.post("/users/" + str(user.id), data=dict(
            username="post_change",
            password="password",
            confirm_password="password",
            role=2
        ), follow_redirects=True)

        self.assertIn("/users/" + str(user.id), result.request.url)
        self.assertEqual(result.status_code, 400)
        old_user = User.query.filter_by(username="pre_change").first()
        updated_user = User.query.filter_by(username="post_change").first()
        self.assertIsNotNone(old_user, "User with previous name still exists")
        self.assertIsNone(updated_user, "User with changed name not updated")

    def test_edit_user_username_already_taken(self):
        """ Edit user with taken username """
        user1 = create_account(username="existing_user", password="password", role=Role.User)
        user2 = User.query.filter_by(username="pre_change").first()
        result = self.client.post("/users/" + str(user2.id), data=dict(
            username=user1.username,  # Use name of reserved Administrator user
            password="password",
            confirm_password="password",
            role=2,
            locale="en"
        ), follow_redirects=True)
        self.assertIn("/users/" + str(user2.id), result.request.url)
        self.assertEqual(result.status_code, 400)
        old_user = User.query.filter_by(username="pre_change").first()
        existing_user = User.query.filter_by(username="existing_user").first()
        self.assertIsNotNone(old_user, "User with previous name still exists")
        self.assertEqual(existing_user.id, user1.id, "Existing user is unchanged")

    def test_edit_user_passwords_unequal(self):
        """ Passwords don't match when editing user """
        user = User.query.filter_by(username="pre_change").first()
        result = self.client.post("/users/" + str(user.id), data=dict(
            username="post_change",
            password="password",
            confirm_password="other_password",
            role=2,
            locale="en",
        ), follow_redirects=True)

        self.assertIn("/users/" + str(user.id), result.request.url)
        self.assertEqual(result.status_code, 400)
        old_user = User.query.filter_by(username="pre_change").first()
        self.assertIsNotNone(old_user, "User with previous name still exists")


if __name__ == '__main__':
    unittest.main()
