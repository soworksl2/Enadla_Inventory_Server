import sys
import unittest
from unittest.mock import patch

sys.argv.append('DEBUG')

from core import create_app
from tests.integration_tests.helper import clear_firebase_operations

class TestGetLastClientVersionAction(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        clear_firebase_operations.clear_tests_from_auth_db()
        clear_firebase_operations.clear_tests_collecion_from_firestore()

        app_server = create_app.create()

        app_server.config.update({
            "TESTING": True
        })
        cls.flask_test_client = app_server.test_client()

    def tearDown(self) -> None:
        clear_firebase_operations.clear_tests_from_auth_db()
        clear_firebase_operations.clear_tests_collecion_from_firestore()

        return super().tearDown()

    # *-*-*-*-*-*-*-*-*-*- tests *-*-*-*-*-*-*-*-*-*-

    def test_given_valid_request_then_return_the_valid_last_client_versio(self):
        with patch('core.app_constants.get_last_client_version') as mock_get_last_client_version:
            #arrange
            mock_get_last_client_version.return_value = (1, 0, 1)

            #act
            r = self.flask_test_client.get('/versions/last_client_version/')

            #asserts
            self.assertEqual(r.status_code, 200)
            self.assertEqual(r.json['last_client_version'], '1.0.1')

    #*-*-**-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-

if __name__ == '__main__':
    sys.argv.pop()
    unittest.main()