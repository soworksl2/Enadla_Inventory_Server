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
from helper import clear_firebase_operations, faker_user_info_data

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

    def create_new_user_info(self, email_number = 1, force_verified = True):
        request_body = helper.process_and_add_slfs({
            'user_info': faker_user_info_data.generate_good_user_info(email_number)
        })

        r = self.flask_test_client.post('/accounts/', json=request_body)
        uid = r.json['updated_user_info']['uid']

        auth.update_user(uid, email_verified=True)

    def get_custom_id_token(self, email_number = 1):
        user_info_regisered = faker_user_info_data.generate_good_user_info(email_number)
        request_body = helper.process_and_add_slfs({
            'email': user_info_regisered['email'],
            'password': user_info_regisered['password']
        })

        r = self.flask_test_client.get('/accounts/auth/', json=request_body)

        return r.json['custom_id_token']

    #-*-*-*-*-*-*-*-*-*-*-*-*-*-*-* tests -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

    def test_given_wrong_slfs_then_error_code_is_HTTP_BASIC_ERROR(self):
        #arrange
        self.create_new_user_info()
        custom_id_token = self.get_custom_id_token()
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
        self.create_new_user_info()
        custom_id_token = self.get_custom_id_token()
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
        self.create_new_user_info(1)
        custom_id_token = self.get_custom_id_token(1)
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