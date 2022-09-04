import os
import sys
import unittest

import requests

#region adding the project path to the sys.path
directory = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(directory)
parent = os.path.dirname(parent)
sys.path.append(parent)
#endregion

import helper
import app_error_code
from helper import clear_firebase_operations, faker_user_info_data

SIGNUP_ACTION_URL = 'http://127.0.0.1:8080/accounts/'

class TestSignUpAction(unittest.TestCase):
    
    def tearDown(self) -> None:
        clear_firebase_operations.clear_tests_from_auth_db()
        clear_firebase_operations.clear_tests_collecion_from_firestore()

        return super().tearDown()

    def test_given_wrong_slfs_then_return_bad_request(self):
        #arrange
        request_body = helper.process_and_add_slfs({
            'user_info': faker_user_info_data.generate_good_user_info()
        })
        request_body['slfs'] = 'wrong_slfs'

        #act
        r = requests.post(url=SIGNUP_ACTION_URL,json=request_body)
        
        #assert
        self.assertEqual(r.status_code, 400)

    def test_given_invalid_user_info_then_error_code_is_INVALID_USERINFO(self):
        #arrange
        invalid_user_info = faker_user_info_data.generate_good_user_info()
        
        del invalid_user_info['password']

        request_body = helper.process_and_add_slfs({
            'user_info': invalid_user_info
        })

        #act
        r = requests.post(url=SIGNUP_ACTION_URL, json=request_body)

        #assert
        error_code = r.json()['error_code']

        self.assertEqual(r.status_code, 400)
        self.assertEqual(error_code, app_error_code.INVALID_USERINFO)

    def test_given_email_conflict_then_error_code_is_EMAIL_CONFLICT(self):
        #arrange
        request_body = helper.process_and_add_slfs({'user_info': faker_user_info_data.generate_good_user_info(email_number=2)})

        #act
        requests.post(url=SIGNUP_ACTION_URL, json=request_body)
        r = requests.post(url=SIGNUP_ACTION_URL, json=request_body)

        #assert
        error_code = r.json()['error_code']

        self.assertEqual(error_code, app_error_code.EMAIL_CONFLICT)

if __name__ == '__main__':
    unittest.main()