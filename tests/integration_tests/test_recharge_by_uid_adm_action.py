from datetime import datetime, timedelta
import os
import sys
import unittest

import pytz

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
from database import token_information_operations
import app_constants
import app_error_code
from helper import clear_firebase_operations, database_helper

class TestRechargeByUidAdm(unittest.TestCase):

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

    #region custom asserts

    def assertDates(self, first_date, second_date, variation = None):
        if not variation:
            self.assertEqual(first_date, second_date)
            return

        min_posible_date = first_date - variation
        max_posible_date = first_date + variation

        self.assertTrue(second_date >= min_posible_date and second_date <= max_posible_date)

    #endregion

    #-*-*-*-*-*-*-*-*-*-*-*-*-*-*-* tests -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

    #si todo esta bien recargar*
    #si el uid no existe entonces error*
    #si el monto es menor a 0 entonces error*
    #si el monto no es un numero entonces error*
    #si el api admin key es invalida entonces error*

    def test_given_valid_request_then_recharge(self):
        #arrange
        uid = database_helper.signUp(self.flask_test_client)
        amount_to_recharge = 5
        api_admin_key = app_constants.get_api_admin_key()

        request_body = {
            'api_admin_key': api_admin_key,
            'uid': uid,
            'amount': amount_to_recharge
        }

        #act
        r = self.flask_test_client.post('/token_information/recharge_by_uid_adm/', json=request_body)

        #assert
        current_token_information = token_information_operations.get_token_information_by_id(uid)

        self.assertEqual(r.status_code, 200)
        self.assertEqual(current_token_information.amount_of_tokens, app_constants.get_init_tokens_on_signUp() + amount_to_recharge)
        self.assertDates(current_token_information.datetime_last_token_recharge, datetime.now(tz=pytz.utc), timedelta(minutes=1))

    def test_given_nonexistent_uid_then_error_code_is_USER_NOT_EXISTS_OR_DISABLE(self):
        #arrange
        nonexistent_uid = 'tests_noexistent_uid'
        amount_to_recharge = 5
        api_admin_key = app_constants.get_api_admin_key()

        request_body = {
            'api_admin_key': api_admin_key,
            'uid': nonexistent_uid,
            'amount': amount_to_recharge
        }

        #act
        r = self.flask_test_client.post('/token_information/recharge_by_uid_adm/', json=request_body)

        #assert
        self.assertEqual(r.status_code, 404)

        error_code = r.json['error_code']
        self.assertEqual(error_code, app_error_code.USER_NOT_EXISTS_OR_DISABLE)

    def test_given_negative_numbers_in_amount_then_HTTP_BASIC_ERROR(self):
        #arrange
        uid = database_helper.signUp(self.flask_test_client)
        amount_to_recharge = -5
        api_admin_key = app_constants.get_api_admin_key()

        request_body = {
            'api_admin_key': api_admin_key,
            'uid': uid,
            'amount': amount_to_recharge
        }

        #act
        r = self.flask_test_client.post('/token_information/recharge_by_uid_adm/', json=request_body)

        #assert
        self.assertEqual(r.status_code, 400)

        error_code = r.json['error_code']
        self.assertEqual(error_code, app_error_code.HTTP_BASIC_ERROR)

    def test_given_wrong_amount_then_HTTP_BASIC_ERROR(self):
        #arrange
        uid = database_helper.signUp(self.flask_test_client)
        amount_to_recharge = 'wrong'
        api_admin_key = app_constants.get_api_admin_key()

        request_body = {
            'api_admin_key': api_admin_key,
            'uid': uid,
            'amount': amount_to_recharge
        }

        #act
        r = self.flask_test_client.post('/token_information/recharge_by_uid_adm/', json=request_body)

        #asserts
        self.assertEqual(r.status_code, 400)
        
        error_code = r.json['error_code']
        self.assertEqual(error_code, app_error_code.HTTP_BASIC_ERROR)

    def test_given_invalid_api_admin_key_then_error_code_is_INVALID_API_ADMIN_KEY(self):
        #arrange
        uid = database_helper.signUp(self.flask_test_client)
        amount_to_recharge = 5
        api_admin_key = 'wrong_api_admin_key'

        request_body = {
            'api_admin_key': api_admin_key,
            'uid': uid,
            'amount': amount_to_recharge
        }

        #act
        r = self.flask_test_client.post('/token_information/recharge_by_uid_adm/', json=request_body)

        #asserts
        self.assertEqual(r.status_code, 401)
        
        error_code = r.json['error_code']
        self.assertEqual(error_code, app_error_code.INVALID_API_ADMIN_KEY)

    #-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

if __name__ == '__main__':
    sys.argv.pop()
    unittest.main()