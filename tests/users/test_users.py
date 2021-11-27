import unittest
from tests import DatabaseTestCase

from kunsthandel.models import Role, User, create_account


class TestLoginLogout(DatabaseTestCase):

    def test_login_redirect(self):
        """ Test if any route redirects to login """
        result = self.client.get("/home")
        self.assertEqual(302, result.status_code)
        self.assertIn("/login", result.headers["Location"])

    def test_login_page(self):
        """ Show Login Page """
        result = self.client.get("/login")
        self.assertEqual(200, result.status_code)

    def test_login_page_logged_in(self):
        """ Test redirect to home page as logged in user """
        self._login_user(Role.User)
        result = self.client.get("/login")
        self.assertEqual(302, result.status_code)
        self.assertIn("/home", result.headers["Location"])

    def test_successful_login(self):
        """ Login with correct data """
        self._insert_user("test", "password", Role.Administrator)
        result = self.client.post("/login", data=dict(
            username="test",
            password="password"
        ), follow_redirects=True)
        self.assertEqual(200, result.status_code)
        self.assertIn("Login successful", str(result.data))

    def test_failed_login(self):
        """ Login with wrong password """
        self._insert_user("test", "password", Role.Administrator)
        result = self.client.post("/login", data=dict(
            username="test",
            password="wrongpassword"
        ), follow_redirects=True)
        self.assertEqual(401, result.status_code)
        self.assertIn("Login unsuccessful", str(result.data))

    def test_invalidated_login(self):
        """ Login with missing password """
        self._insert_user("test", "password", Role.Administrator)
        result = self.client.post("/login", data=dict(
            username="test"
        ), follow_redirects=True)
        self.assertEqual(400, result.status_code)
        self.assertIn("This field is required.", str(result.data))

    def test_logout_not_logged_in(self):
        """ Logout works when not logged in """
        result = self.client.get("/logout")
        self.assertEqual(302, result.status_code)  # Should redirect to login
        self.assertIn("/login", result.headers["Location"])

    def test_logout(self):
        """ Logout works when logged in """
        self._login_user(Role.External)
        result = self.client.get("/logout")
        self.assertEqual(302, result.status_code)  # Should redirect to login
        self.assertIn("/login", result.headers["Location"])


class TestUserPermissions(DatabaseTestCase):

    def test_permission_edit_own_user(self):
        """ Check roles for permission to edit own profile """
        pairs = {Role.External: 403, Role.Visitor: 403, Role.User: 200, Role.Editor: 200, Role.Administrator: 200}
        for role, status in pairs.items():
            with self.subTest(role=role.name):
                self._login_user(role=role, username=f"test_{role.name}")
                result = self.client.get("/users/me")
                self.assertEqual(status, result.status_code)
                self._logout()

    def test_permission_edit_user(self):
        """ Check roles for permission to edit user profiles """
        pairs = {Role.External: 403, Role.Visitor: 403, Role.User: 403, Role.Editor: 403, Role.Administrator: 200}
        for role, status in pairs.items():
            with self.subTest(role=role.name):
                user = self._login_user(role=role, username=f"test_{role.name}")
                result = self.client.get(f"/users/{user.id}")
                self.assertEqual(status, result.status_code)
                self._logout()

    def test_permission_create_user(self):
        """ Check roles for permission to create user profiles """
        pairs = {Role.External: 403, Role.Visitor: 403, Role.User: 403, Role.Editor: 403, Role.Administrator: 200}
        for role, status in pairs.items():
            with self.subTest(role=role.name):
                self._login_user(role=role, username=f"test_{role.name}")
                result = self.client.get("/users/create")
                self.assertEqual(status, result.status_code)
                self._logout()

    def test_permission_delete_user(self):
        """ Check roles for permission to delete user profiles """
        pairs = {Role.External: 403, Role.Visitor: 403, Role.User: 403, Role.Editor: 403, Role.Administrator: 302}
        for role, status in pairs.items():
            with self.subTest(role=role.name):
                user = self._login_user(role=role, username=f"test_{role.name}")
                result = self.client.post(f"/users/{user.id}/delete")
                self.assertEqual(status, result.status_code)
                self._logout()

    def test_permission_users(self):
        """ Check roles for permission to view users overview """
        pairs = {Role.External: 403, Role.Visitor: 403, Role.User: 403, Role.Editor: 403, Role.Administrator: 200}
        for role, status in pairs.items():
            with self.subTest(role=role.name):
                user = self._login_user(role=role, username=f"test_{role.name}")
                result = self.client.get("/users")
                self.assertEqual(status, result.status_code)
                self._logout()


class TestCreateUser(DatabaseTestCase):

    def setUp(self):
        super(TestCreateUser, self).setUp()
        admin = self._login_user(Role.Administrator, username="Administrator")

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
        self.assertEqual(200, result.status_code)
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
        self.assertEqual("/users/create", result.request.path)  # Not optimal, /users is also in /users/create
        self.assertEqual(200, result.status_code)
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

        self.assertEqual("/users/create", result.request.path)
        self.assertEqual(400, result.status_code)
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
        self.assertEqual("/users/create", result.request.path)
        self.assertEqual(400, result.status_code)

    def test_create_user_passwords_unequal(self):
        """ Passwords don't match """
        result = self.client.post("/users/create", data=dict(
            username="test",
            password="password",
            confirm_password="other_password",
            role=2,
            locale="en"
        ), follow_redirects=True)

        self.assertEqual("/users/create", result.request.path)
        self.assertEqual(400, result.status_code)
        created_user = User.query.filter_by(username="test").first()
        self.assertIsNone(created_user, "User does not exists in database, as creation failed")


class TestEditOwnUser(DatabaseTestCase):

    def test_edit_own_user_successful(self):
        """ Edit own locale by user """
        self._login_user(role=Role.User, username="user")
        result = self.client.post("/users/me", data=dict(
            password="new_password",
            confirm_password="new_password",
            locale="de"
        ), follow_redirects=True)

        self.assertEqual("/users/me", result.request.path)
        self.assertEqual(200, result.status_code)
        user = User.query.filter_by(username="user").first()
        self.assertEqual("de", user.locale, "User locale has been updated")

    def test_edit_own_user_missing_parameter(self):
        """ Missing parameter on own editing """
        self._login_user(role=Role.User, username="user")
        result = self.client.post("/users/me", data=dict(
            password="new_password",
            confirm_password="new_password"
        ), follow_redirects=True)

        self.assertEqual("/users/me", result.request.path)
        self.assertEqual(400, result.status_code)
        user = User.query.filter_by(username="user").first()
        self.assertEqual(user.locale, "en", "User locale has not been updated")

    def test_edit_own_user_passwords_unequal(self):
        """ not matching passwords on editing own user """
        self._login_user(role=Role.User, username="user")
        result = self.client.post("/users/me", data=dict(
            password="new_password",
            confirm_password="other_password",
            locale="de"
        ), follow_redirects=True)

        self.assertEqual("/users/me", result.request.path)
        self.assertEqual(400, result.status_code)
        user = User.query.filter_by(username="user").first()
        self.assertEqual(user.locale, "en", "User locale has not been updated")


class TestEditUser(DatabaseTestCase):

    def setUp(self):
        super(TestEditUser, self).setUp()
        admin = self._login_user(Role.Administrator, username="Administrator")
        user = self._insert_user(username="pre_change", password="password", role=Role.User)

    def test_edit_user_successful(self):
        """ Edit username by an Administrator """
        user = User.query.filter_by(username="pre_change").first()
        result = self.client.post(f"/users/{user.id}", data=dict(
            username="post_change",
            password="password",
            confirm_password="password",
            role=2,
            locale="en"
        ), follow_redirects=True)

        self.assertEqual("/users", result.request.path)
        self.assertEqual(200, result.status_code)
        old_user = User.query.filter_by(username="pre_change").first()
        updated_user = User.query.filter_by(username="post_change").first()
        self.assertIsNone(old_user, "User with previous name doesn't exists in database")
        self.assertIsNotNone(updated_user, "User with changed name exists in database")

    def test_edit_user_missing_parameter(self):
        """ Missing locale parameter """
        user = User.query.filter_by(username="pre_change").first()
        result = self.client.post(f"/users/{user.id}", data=dict(
            username="post_change",
            password="password",
            confirm_password="password",
            role=2
        ), follow_redirects=True)

        self.assertEqual(f"/users/{user.id}", result.request.path)
        self.assertEqual(400, result.status_code)
        old_user = User.query.filter_by(username="pre_change").first()
        updated_user = User.query.filter_by(username="post_change").first()
        self.assertIsNotNone(old_user, "User with previous name still exists")
        self.assertIsNone(updated_user, "User with changed name not updated")

    def test_edit_user_username_already_taken(self):
        """ Edit user with taken username """
        user1 = create_account(username="existing_user", password="password", role=Role.User)
        user2 = User.query.filter_by(username="pre_change").first()
        result = self.client.post(f"/users/{user2.id}", data=dict(
            username=user1.username,  # Use name of reserved Administrator user
            password="password",
            confirm_password="password",
            role=2,
            locale="en"
        ), follow_redirects=True)
        self.assertEqual(f"/users/{user2.id}", result.request.path)
        self.assertEqual(400, result.status_code)
        old_user = User.query.filter_by(username="pre_change").first()
        existing_user = User.query.filter_by(username="existing_user").first()
        self.assertIsNotNone(old_user, "User with previous name still exists")
        self.assertEqual(user1.id, existing_user.id, "Existing user is unchanged")

    def test_edit_user_passwords_unequal(self):
        """ Passwords don't match when editing user """
        user = User.query.filter_by(username="pre_change").first()
        result = self.client.post(f"/users/{user.id}", data=dict(
            username="post_change",
            password="password",
            confirm_password="other_password",
            role=2,
            locale="en",
        ), follow_redirects=True)

        self.assertEqual(f"/users/{user.id}", result.request.path)
        self.assertEqual(400, result.status_code)
        old_user = User.query.filter_by(username="pre_change").first()
        self.assertIsNotNone(old_user, "User with previous name still exists")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
