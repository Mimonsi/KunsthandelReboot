import unittest

from flask import current_app
from werkzeug.datastructures import FileStorage

from kunsthandel import db
from kunsthandel.generic_type.routes import MODELS
from tests import DatabaseTestCase

from kunsthandel.models import Role, Item, Type, Location, Origin


class TestGenericTypePermissions(DatabaseTestCase):

    def setUp(self):
        super(TestGenericTypePermissions, self).setUp()
        for name, model in MODELS.items():
            db.session.add(model(name=f"test_{name}"))
        db.session.commit()

    def test_permission_generic_types(self):
        """ Check roles for permission to generic type overview """
        pairs = {Role.External: 403, Role.Visitor: 403, Role.User: 200, Role.Editor: 200, Role.Administrator: 200}
        for role, status in pairs.items():
            self._login_user(role, f"test_{role.name}")
            for name, model in MODELS.items():
                with self.subTest(role.name, model_name=name):
                    result = self.client.get(f"/{name}")
                    self.assertEqual(status, result.status_code)
            self._logout()

    def test_permission_generic_type_details(self):
        """ Check roles for permission to view generic type details """
        pairs = {Role.External: 403, Role.Visitor: 403, Role.User: 200, Role.Editor: 200, Role.Administrator: 200}
        for role, status in pairs.items():
            self._login_user(role, f"test_{role.name}")
            for name, model in MODELS.items():
                with self.subTest(role.name, model_name=name):
                    result = self.client.get(f"/{name}/1")
                    self.assertEqual(status, result.status_code)
            self._logout()

    def test_permission_generic_type_create(self):
        """ Check roles for permission to view generic type create """
        pairs = {Role.External: 403, Role.Visitor: 403, Role.User: 403, Role.Editor: 200, Role.Administrator: 200}
        for role, status in pairs.items():
            self._login_user(role, f"test_{role.name}")
            for name, model in MODELS.items():
                with self.subTest(role.name, model_name=name):
                    result = self.client.get(f"/{name}/create")
                    self.assertEqual(status, result.status_code)
            self._logout()

    def test_permission_generic_type_edit(self):
        """ Check roles for permission to view generic type edit """
        pairs = {Role.External: 403, Role.Visitor: 403, Role.User: 403, Role.Editor: 200, Role.Administrator: 200}
        for role, status in pairs.items():
            self._login_user(role, f"test_{role.name}")
            for name, model in MODELS.items():
                with self.subTest(role.name, model_name=name):
                    result = self.client.get(f"/{name}/1/edit")
                    self.assertEqual(status, result.status_code)
            self._logout()


class TestCreateGenericType(DatabaseTestCase):
    def setUp(self):
        super(TestCreateGenericType, self).setUp()
        admin = self._login_user(Role.Administrator, username="Administrator")

    def test_create_generic_type_successful(self):
        """ Create new generic type dataset by an Administrator """
        for name, model in MODELS.items():
            with self.subTest(name):
                result = self.client.post(f"/{name}/create", data=dict(
                    name=f"test_{name}",
                ), follow_redirects=True)
                self.assertEqual(200, result.status_code)
                self.assertEqual(f"/{name}", result.request.path)
                self.assertEqual(1, model.query.count())
                self.assertIsNotNone(model.query.first())
                self.assertEqual(f"test_{name}", model.query.first().name)

    def test_create_generic_type_missing_name(self):
        """ Create new generic type dataset by an Administrator """
        for name, model in MODELS.items():
            with self.subTest(name):
                result = self.client.post(f"/{name}/create", follow_redirects=True)
                self.assertEqual(f"/{name}/create", result.request.path)
                self.assertEqual(400, result.status_code)
                self.assertEqual(0, model.query.count())
                self.assertIsNone(model.query.first())


class TestInvalidModel(DatabaseTestCase):
    def setUp(self):
        super(TestInvalidModel, self).setUp()
        admin = self._login_user(Role.Administrator, username="Administrator")

    def test_generic_item_models_invalid_model(self):
        result = self.client.get("/test_model")
        self.assertEqual(404, result.status_code)

    def test_create_generic_item_model_invalid_model(self):
        result = self.client.get("/test_model/create")
        self.assertEqual(404, result.status_code)

    def test_generic_item_details_model_invalid_model(self):
        result = self.client.get("/test_model/1")
        self.assertEqual(404, result.status_code)

    def test_edit_generic_item_model_invalid_model(self):
        result = self.client.get("/test_model/1/edit")
        self.assertEqual(404, result.status_code)


class TestInvalidMethods(DatabaseTestCase):
    def setUp(self):
        super(TestInvalidMethods, self).setUp()
        admin = self._login_user(Role.Administrator, username="Administrator")

    def test_generic_types_post(self):
        """ Route should not accept post """
        for name, model in MODELS.items():
            with self.subTest(name):
                result = self.client.post(f"/{name}", follow_redirects=True)
                self.assertEqual(405, result.status_code)

    def test_generic_type_details_post(self):
        """ Route should not accept post """
        for name, model in MODELS.items():
            with self.subTest(name):
                result = self.client.post(f"/{name}/1", follow_redirects=True)
                self.assertEqual(405, result.status_code)


class TestEditGenericType(DatabaseTestCase):

    def setUp(self):
        super(TestEditGenericType, self).setUp()
        for name, model in MODELS.items():
            db.session.add(model(name=f"test_{name}"))
        db.session.commit()
        admin = self._login_user(Role.Administrator, username="Administrator")

    def test_edit_generic_type_successful(self):
        """ Edit generic type dataset by an Administrator """
        for name, model in MODELS.items():
            with self.subTest(name):
                result = self.client.post(f"/{name}/1/edit", data=dict(
                    name=f"afterRename_{name}",
                ), follow_redirects=True)
                self.assertEqual(200, result.status_code)
                self.assertEqual(1, model.query.count())
                self.assertIsNotNone(model.query.filter_by(name=f"afterRename_{name}").first())
                self.assertEqual(f"afterRename_{name}", model.query.first().name)

    def test_edit_generic_type_missing_name(self):
        """ Create new generic type dataset by an Administrator """
        for name, model in MODELS.items():
            with self.subTest(name):
                result = self.client.post(f"/{name}/1/edit", follow_redirects=True)
                self.assertEqual(400, result.status_code)
                self.assertEqual(1, model.query.count())
                self.assertIsNone(model.query.filter_by(name=f"afterRename_{name}").first())
                self.assertEqual(f"test_{name}", model.query.first().name)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
