import unittest

from kunsthandel import create_app, db, config
from kunsthandel.models import Role, create_account


class DatabaseTestCase(unittest.TestCase):

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

    @staticmethod
    def _insert_user(username, password, role=Role.External):
        return create_account(username=username, password=password, role=role)

    def _logout(self):
        self.client.get("/logout")
