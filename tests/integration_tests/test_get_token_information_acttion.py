import os
import sys
import unittest

#region adding src folder to sys.path
root_path = os.path.dirname(os.path.realpath(__file__))
root_path = os.path.dirname(root_path)
root_path = os.path.dirname(root_path)
src_path = os.path.join(root_path, 'src')
sys.path.append(src_path)
#endregion

sys.argv.append('DEBUG')

from app import app_server

from own_firebase_admin import auth
import helper
import app_error_code
import app_constants
from helper import clear_firebase_operations, database_helper

class TestGetTokenInformationAction(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        clear_firebase_operations.clear_tests_from_auth_db()
        clear_firebase_operations.clear_tests_collecion_from_firestore()

        app_server.config.update({
            "TESTING": True
        })
        cls.flask_test_client = app_server.test_client()

    def tearDown(self) -> None:
        clear_firebase_operations.clear_tests_from_auth_db()
        clear_firebase_operations.clear_tests_collecion_from_firestore()

        return super().tearDown()

    #-*-*-*-*-*-*-*-*-*-*-*-*-*-*-* tests -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

    def test_given_wrong_slfs_then_error_code_is_HTTP_BASIC_ERROR(self):
        #arrange
        database_helper.signUp(self.flask_test_client,  force_is_verified=True)
        custom_id_token, _, _ = database_helper.authenticate(self.flask_test_client)
        request_body = {
            'custom_id_token': custom_id_token,
            'lt': 'test',
            'slfs': 'wrong_slfs'
        }

        #act
        r = self.flask_test_client.get('/token_information/', json=request_body)

        #assert
        error_code = r.json['error_code']

        self.assertEqual(r.status_code, 400)
        self.assertEqual(error_code, app_error_code.HTTP_BASIC_ERROR)

    def test_given_no_slfs_then_error_code_is_HTTP_BASIC_ERROR(self):
        #arrange
        database_helper.signUp(self.flask_test_client, force_is_verified=True)
        custom_id_token, _, _ = database_helper.authenticate(self.flask_test_client)
        request_body = {
            'custom_id_token': custom_id_token
        }

        #act
        r = self.flask_test_client.get('/token_information/', json=request_body)

        #assert
        error_code = r.json['error_code']

        self.assertEqual(r.status_code, 400)
        self.assertEqual(error_code, app_error_code.HTTP_BASIC_ERROR)

    def test_given_valid_request_then_return_token_information(self):
        #arrange
        database_helper.signUp(self.flask_test_client, email_number=1, force_is_verified=True)
        custom_id_token, _, _ = database_helper.authenticate(self.flask_test_client, 1)
        request_body = helper.process_and_add_slfs({
            'custom_id_token': custom_id_token
        })

        #act
        r = self.flask_test_client.get('/token_information/', json=request_body)

        #assert
        self.assertIn('token_information', r.json)
        self.assertEqual(r.json['token_information']['amount_of_tokens'], app_constants.get_init_tokens_on_signUp())

    #TODO: make tests for when the custom id token is invalid

    #-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

if __name__ == '__main__':
    sys.argv.pop()
    unittest.main()