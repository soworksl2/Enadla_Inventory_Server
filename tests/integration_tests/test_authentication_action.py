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

import helper
import app_error_code
from helper import clear_firebase_operations, faker_user_info_data

class TestAuthenticationAction(unittest.TestCase):

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
        request_body = {
            'email': faker_user_info_data.get_test_email(1),
            'password': 'testing',
            'lt': 'test',
            'slfs': 'wrong_slfs'
        }

        #act
        r = self.flask_test_client.get('/accounts/auth/', json=request_body)

        #assert
        error_code = r.json['error_code']

        self.assertEqual(r.status_code, 400)
        self.assertEqual(error_code, app_error_code.HTTP_BASIC_ERROR)

    def test_given_no_slfs_then_error_code_is_HTTP_BASIC_ERROR(self):
        #arrange
        request_body = {
            'email': faker_user_info_data.get_test_email(1),
            'password': 'testing'
        }

        #act
        r = self.flask_test_client.get('/accounts/auth/', json=request_body)

        #assert
        error_code = r.json['error_code']

        self.assertEqual(r.status_code, 400)
        self.assertEqual(error_code, app_error_code.HTTP_BASIC_ERROR)

    def test_given_valid_credentials_then_authenticate(self):
        #arrange
        new_user = faker_user_info_data.generate_good_user_info(1)
        new_user['password'] = 'testing'
        new_user_request_body = helper.process_and_add_slfs({
            'user_info': new_user
        })
        self.flask_test_client.post('/accounts/', json=new_user_request_body)

        request_body = helper.process_and_add_slfs({
            'email': faker_user_info_data.get_test_email(1),
            'password': new_user['password']
        })
        
        #act
        r = self.flask_test_client.get('/accounts/auth/', json=request_body)

        #assert
        self.assertEqual(r.status_code, 200)
        self.assertTrue('custom_id_token' in r.json)
        self.assertTrue('refresh_token' in r.json)
        self.assertTrue('user_info' in r.json)

    def test_given_no_email_then_bad_request(self):
        #arrange
        request_body = helper.process_and_add_slfs({
            'email': '',
            'password': 'testing'
        })

        #act
        r = self.flask_test_client.get('/accounts/auth/', json=request_body)

        #assert
        error_code = r.json['error_code']

        self.assertEqual(r.status_code, 400)
        self.assertEqual(error_code, app_error_code.HTTP_BASIC_ERROR)

    def test_given_no_password_then_bad_request(self):
        #arrange
        request_body = helper.process_and_add_slfs({
            'email': faker_user_info_data.get_test_email(1),
            'password': ''
        })

        #act
        r = self.flask_test_client.get('/accounts/auth/', json=request_body)

        #assert
        error_code = r.json['error_code']

        self.assertEqual(r.status_code, 400)
        self.assertEqual(error_code, app_error_code.HTTP_BASIC_ERROR)

    def test_given_invalid_email_then_error_code_is_INVALID_CREDENTIALS(self):
        #arrange
        new_user = faker_user_info_data.generate_good_user_info(1)
        new_user['password'] = 'testing'
        new_user_request_body = helper.process_and_add_slfs({
            'user_info': new_user
        })
        self.flask_test_client.post('/accounts/', json=new_user_request_body)

        request_body = helper.process_and_add_slfs({
            'email': 'invalid.email@gmail.com',
            'password': new_user['password']
        })

        #act
        r = self.flask_test_client.get('/accounts/auth/', json=request_body)

        #assert
        error_code = r.json['error_code']

        self.assertEqual(error_code, app_error_code.INVALID_CREDENTIALS)

    def test_given_invalid_password_then_error_code_is_INVALID_CREDENTIALS(self):
        #arrange
        new_user = faker_user_info_data.generate_good_user_info(1)
        new_user['password'] = 'testing'
        new_user_request_body = helper.process_and_add_slfs({
            'user_info': new_user
        })
        self.flask_test_client.post('/accounts/', json=new_user_request_body)

        request_body = helper.process_and_add_slfs({
            'email': new_user['email'],
            'password': 'invalid_password'
        })

        #act
        r = self.flask_test_client.get('/accounts/auth/', json=request_body)

        #assert
        error_code = r.json['error_code']

        self.assertEqual(error_code, app_error_code.INVALID_CREDENTIALS)

    #-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

if __name__ == '__main__':
    sys.argv.pop()
    unittest.main()