import unittest

from tests import DatabaseTestCase


class TestRoleRequiredDecorator(DatabaseTestCase):
    def test_no_permission(self):
        pass


if __name__ == "__main__":
    unittest.main()
