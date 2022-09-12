import os
import sys
import unittest
from unittest.mock import patch

#region adding src folder to sys.path
root_path = os.path.dirname(os.path.realpath(__file__))
root_path = os.path.dirname(root_path)
root_path = os.path.dirname(root_path)
src_path = os.path.join(root_path, 'src')
sys.path.append(src_path)
#endregion

sys.argv.append('DEBUG')

import helper
import app_error_code
import app_constants
from app import app_server
from database import token_information_operations, auth_db_operations
from helper import database_helper
from helper import clear_firebase_operations

class TestBuyBalanceStatusKeyAction(unittest.TestCase):

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

    # *-*-*-*-*-*-*-*-*-*- tests *-*-*-*-*-*-*-*-*-*-

    def test_given_wrong_slfs_then_error_is_HTTP_BASIC_ERROR(self):
        #arrange
        database_helper.signUp(self.flask_test_client, force_is_verified=True)
        custom_id_token, _, _ = database_helper.authenticate(self.flask_test_client)
        request_body = {
            'custom_id_token': custom_id_token,
            'balance_key': 'test_balance_key',
            'lt': 'test',
            'slfs': 'wrong_slfs'
        }

        #act
        r = self.flask_test_client.get('/shop/get_balance_status_key/', json=request_body)

        #assert
        error_code = r.json['error_code']

        self.assertEqual(r.status_code, 400)
        self.assertEqual(error_code, app_error_code.HTTP_BASIC_ERROR)

    def test_given_no_slfs_then_error_is_HTTP_BASIC_ERROR(self):
        #arrange
        database_helper.signUp(self.flask_test_client, force_is_verified=True)
        custom_id_token, _, _ = database_helper.authenticate(self.flask_test_client)
        request_body = {
            'custom_id_token': custom_id_token,
            'balance_key': 'test_balance_key'
        }

        #act
        r = self.flask_test_client.get('/shop/get_balance_status_key/', json=request_body)

        #assert
        error_code = r.json['error_code']

        self.assertEqual(r.status_code, 400)
        self.assertEqual(error_code, app_error_code.HTTP_BASIC_ERROR)

    def test_given_sufficient_tokens_then_buy_correctly(self):
        variable_config_for_tests = [(2, 1), (3, 1), (1, 0), (2, 0)]

        for init_tokens_on_signup, balance_status_key_price in variable_config_for_tests:                
            with \
                patch('app_constants.get_balance_status_key_price') as mock_balance_status_key_price,\
                patch('app_constants.get_init_tokens_on_signUp') as mock_init_tokens_on_signUp:

                mock_balance_status_key_price.return_value = balance_status_key_price
                mock_init_tokens_on_signUp.return_value = init_tokens_on_signup
                
                with self.subTest(init_tokens_on_signup=init_tokens_on_signup, balance_status_key_price=balance_status_key_price):
                    clear_firebase_operations.clear_tests_from_auth_db()
                    clear_firebase_operations.clear_tests_collecion_from_firestore()

                    #arrange
                    database_helper.signUp(self.flask_test_client, force_is_verified=True)
                    custom_id_token, _, _ = database_helper.authenticate(self.flask_test_client)

                    request_body = helper.process_and_add_slfs({
                        'custom_id_token': custom_id_token,
                        'balance_key': 'test_balance_key'
                    })

                    #act
                    r = self.flask_test_client.get('/shop/get_balance_status_key/', json=request_body)

                    #assert
                    self.assertEqual(r.status_code, 200)
                    self.assertTrue('balance_status_key' in r.json)
                    balance_status_key_lenght = len(r.json['balance_status_key'])
                    self.assertTrue(balance_status_key_lenght > 0)

                    firebase_id_token, _ = auth_db_operations.process_custom_id_token(custom_id_token)
                    firebase_id_token_decoded = auth_db_operations.verify_firebase_id_token(firebase_id_token)
                    current_token_information_after = token_information_operations.get_token_information_by_id(firebase_id_token_decoded['uid'])
                    self.assertEqual(current_token_information_after.amount_of_tokens, init_tokens_on_signup - balance_status_key_price)

    def test_given_insufficient_tokens_then_error_code_is_INSUFFICIENT_TOKENS(self):
        
        variables_config_for_tests = [(0, 1), (0, 2), (1, 2), (1, 3), (2, 3)]

        for init_tokens_on_signup, balance_status_key_price in variables_config_for_tests:
            with \
                patch('app_constants.get_balance_status_key_price') as mock_balance_status_key_price,\
                patch('app_constants.get_init_tokens_on_signUp') as mock_init_tokens_on_signUp:

                mock_init_tokens_on_signUp.return_value = init_tokens_on_signup
                mock_balance_status_key_price.return_value = balance_status_key_price

                with self.subTest(init_tokens_on_signup=init_tokens_on_signup, balance_status_key_price=balance_status_key_price):
                    clear_firebase_operations.clear_tests_from_auth_db()
                    clear_firebase_operations.clear_tests_collecion_from_firestore()

                    #arrange
                    database_helper.signUp(self.flask_test_client, force_is_verified=True)
                    custom_id_token, _, _ = database_helper.authenticate(self.flask_test_client)

                    request_body = helper.process_and_add_slfs({
                        'custom_id_token': custom_id_token,
                        'balance_key': 'test_balance_key'
                    })

                    #act
                    r = self.flask_test_client.get('/shop/get_balance_status_key/', json=request_body)

                    #asserts
                    error_code = r.json['error_code']

                    self.assertEqual(r.status_code, 409)
                    self.assertEqual(error_code, app_error_code.INSUFFICIENT_TOKENS)

                    firebase_id_token, _ = auth_db_operations.process_custom_id_token(custom_id_token)
                    firebase_id_token_decoded = auth_db_operations.verify_firebase_id_token(firebase_id_token)
                    current_token_information_after = token_information_operations.get_token_information_by_id(firebase_id_token_decoded['uid'])
                    self.assertEqual(current_token_information_after.amount_of_tokens, init_tokens_on_signup)

    def test_given_exact_amount_of_tokens_then_buy_correctly(self):

        variables_config_for_tests = [(0, 0), (1, 1), (2, 2)]

        for init_tokens_on_signup, balance_status_key_price in variables_config_for_tests:
            with \
                patch('app_constants.get_balance_status_key_price') as mock_balance_status_key_price,\
                patch('app_constants.get_init_tokens_on_signUp') as mock_init_tokens_on_signUp:

                mock_init_tokens_on_signUp.return_value = init_tokens_on_signup
                mock_balance_status_key_price.return_value = balance_status_key_price

                with self.subTest(init_tokens_on_signup=init_tokens_on_signup, balance_status_key_price=balance_status_key_price):
                    clear_firebase_operations.clear_tests_from_auth_db()
                    clear_firebase_operations.clear_tests_collecion_from_firestore()

                    #arrange
                    database_helper.signUp(self.flask_test_client, force_is_verified=True)
                    custom_id_token, _, _ = database_helper.authenticate(self.flask_test_client)

                    request_body = helper.process_and_add_slfs({
                        'custom_id_token': custom_id_token,
                        'balance_key': 'test_balance_key'
                    })

                    #act
                    r = self.flask_test_client.get('/shop/get_balance_status_key/', json=request_body)

                    #asserts
                    self.assertEqual(r.status_code, 200)
                    self.assertTrue('balance_status_key' in r.json)
                    balance_status_key_lenght = len(r.json['balance_status_key'])
                    self.assertTrue(balance_status_key_lenght > 0)

                    firebase_id_token, _ = auth_db_operations.process_custom_id_token(custom_id_token)
                    firebase_id_token_decoded = auth_db_operations.verify_firebase_id_token(firebase_id_token)
                    current_token_information_after = token_information_operations.get_token_information_by_id(firebase_id_token_decoded['uid'])
                    self.assertEqual(current_token_information_after.amount_of_tokens, 0)

    #*-*-**-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-

if __name__ == '__main__':
    sys.argv.pop()
    unittest.main()