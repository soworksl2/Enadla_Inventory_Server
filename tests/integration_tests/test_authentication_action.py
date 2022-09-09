import os
import sys
import unittest
from datetime import datetime, timedelta

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
from own_firebase_admin import db

import helper
import app_error_code
import app_constants
from helper import clear_firebase_operations, faker_user_info_data, database_helper

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

    #region custom asserts

    def assertMachineLink(self, machine_id, email, creation_date_expected):
        machine_links_founds = db.collection('test_machine_links').where('machine_id', '==', machine_id).get()

        self.assertFalse(len(machine_links_founds) <= 0)

        if len(machine_links_founds) <= 0:
            return

        self.assertEqual(machine_links_founds[0].get('email_linked'), email)
        creation_date_min = creation_date_expected - timedelta(minutes=15)
        creation_date_max = creation_date_expected + timedelta(minutes=15)

        creation_date = machine_links_founds[0].get('link_creation_date')
        creation_date_is_aproximately_correct = creation_date >= creation_date_min and creation_date <= creation_date_max

        self.assertTrue(creation_date_is_aproximately_correct)

    #endregion

    #-*-*-*-*-*-*-*-*-*-*-*-*-*-*-* tests -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

    def test_given_wrong_slfs_then_error_code_is_HTTP_BASIC_ERROR(self):
        #arrange
        request_body = {
            'machine_id': 'test_machine',
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
            'machine_id': 'test_machine',
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
            'machine_id': 'test_machine',
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
            'machine_id': 'test_machine',
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
            'machine_id': 'test_machine',
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
            'machine_id': 'test_machine',
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
            'machine_id': 'test_machine1',
            'email': new_user['email'],
            'password': 'invalid_password'
        })

        #act
        r = self.flask_test_client.get('/accounts/auth/', json=request_body)

        #assert
        error_code = r.json['error_code']

        self.assertEqual(error_code, app_error_code.INVALID_CREDENTIALS)

    def test_given_machine_no_linked_yet_and_try_to_authenticate_then_correct(self):
        #this method is almost the same thing than test_given_valid_credentials_then_authenticate
        #and can be avoided
        self.test_given_valid_credentials_then_authenticate()

    def test_given_machine_already_linked_an_try_to_authenticate_itself_then_correct(self):
        #arrange
        database_helper.signUp(self.flask_test_client, 1, custom_password='123456',force_is_verified=True)
        database_helper.authenticate(self.flask_test_client, 1, custom_password='123456', custom_machine_id='test_machine1')

        #act
        request_body = helper.process_and_add_slfs({
            'machine_id': 'test_machine1',
            'email': faker_user_info_data.get_test_email(1),
            'password': '123456'
        })

        r = self.flask_test_client.get('/accounts/auth/', json=request_body)

        #assert
        self.assertEqual(r.status_code, 200)
        self.assertTrue('custom_id_token' in r.json)
        self.assertTrue('refresh_token' in r.json)
        self.assertTrue('user_info' in r.json)
        self.assertMachineLink('test_machine1', faker_user_info_data.get_test_email(1), datetime.now(tz=pytz.utc))

    def test_given_machine_already_linked_and_try_to_authenticate_another_user_then_error_code_MACHINE_LOCKED(self):
        #arrange
        database_helper.signUp(self.flask_test_client, 1, force_is_verified=True)
        database_helper.signUp(self.flask_test_client, 2, custom_password='123456', force_is_verified=True)

        database_helper.authenticate(self.flask_test_client, 1, custom_machine_id='test_machine1')

        #act
        request_body=helper.process_and_add_slfs({
            'machine_id': 'test_machine1',
            'email': faker_user_info_data.get_test_email(2),
            'password': '123456'
        })

        r = self.flask_test_client.get('/accounts/auth/', json=request_body)

        #assert
        error_code = r.json['error_code']

        self.assertEqual(r.status_code, 409)
        self.assertEqual(error_code, app_error_code.LOCKED_MACHINE)
        self.assertMachineLink('test_machine1', faker_user_info_data.get_test_email(1), datetime.now(tz=pytz.utc))

    def test_given_old_machine_already_linked_and_try_to_authenticate_the_same_user_then_allow_it(self):
        #arrange
        locked_time = app_constants.get_machine_link_locked_time()
        new_link_date = datetime.now(tz=pytz.utc) - timedelta(days=locked_time+1)

        database_helper.signUp(self.flask_test_client, 1, '123456', force_is_verified=True)
        database_helper.authenticate(self.flask_test_client, 1, '123456', 'test_machine1')
        database_helper.change_date_of_machine_link('test_machine1', new_link_date)

        #act
        request_body = helper.process_and_add_slfs({
            'machine_id': 'test_machine1',
            'email': faker_user_info_data.get_test_email(1),
            'password': '123456'
        })

        r = self.flask_test_client.get('/accounts/auth/', json=request_body)

        #assert
        self.assertEqual(r.status_code, 200)
        self.assertTrue('custom_id_token' in r.json)
        self.assertTrue('refresh_token' in r.json)
        self.assertTrue('user_info' in r.json)
        self.assertMachineLink('test_machine1', faker_user_info_data.get_test_email(1), new_link_date)

    def test_given_old_machine_already_linked_and_try_to_authenticate_another_user_then_allow_it(self):
        #arrange
        locked_time = app_constants.get_machine_link_locked_time()
        new_link_date = datetime.now(tz=pytz.utc) - timedelta(days=locked_time+1)

        database_helper.signUp(self.flask_test_client, 1, '123456', force_is_verified=True)
        database_helper.signUp(self.flask_test_client, 2, '123456', force_is_verified=True)
        database_helper.authenticate(self.flask_test_client, 1, '123456', 'test_machine1')
        database_helper.change_date_of_machine_link('test_machine1', new_link_date)

        #act
        request_body = helper.process_and_add_slfs({
            'machine_id': 'test_machine1',
            'email': faker_user_info_data.get_test_email(2),
            'password': '123456'
        })

        r = self.flask_test_client.get('/accounts/auth/', json=request_body)

        #assert
        self.assertEqual(r.status_code, 200)
        self.assertTrue('custom_id_token' in r.json)
        self.assertTrue('refresh_token' in r.json)
        self.assertTrue('user_info' in r.json)
        self.assertMachineLink('test_machine1', faker_user_info_data.get_test_email(2), datetime.now(tz=pytz.utc))

    #-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

if __name__ == '__main__':
    sys.argv.pop()
    unittest.main()