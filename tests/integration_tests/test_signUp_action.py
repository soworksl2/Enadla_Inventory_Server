import os
import sys
import unittest
from datetime import datetime, timedelta

import pytz

sys.argv.append('DEBUG')

from core import create_app

from core.own_firebase_admin import db, auth
from tests.integration_tests import helper
from core import app_error_code, app_constants
from tests.integration_tests.helper import clear_firebase_operations, faker_user_info_data
from core.helpers import own_json

class TestSignUpAction(unittest.TestCase):
    
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

    #region custom asserts methods
    def is_correct_creation_date(self, creation_date):
        processed_creation_date = own_json.process_json_obj({'date': creation_date})['date']

        return\
            processed_creation_date > datetime.now(tz=pytz.utc) - timedelta(minutes=15) and\
            processed_creation_date < datetime.now(tz=pytz.utc) + timedelta(minutes=15)

    def assertGoodUpdatedUserInfo(self, updated_user_info, user_info_used):

        self.assertTrue(updated_user_info['uid'])
        self.assertEqual(updated_user_info['email'], user_info_used['email'])
        self.assertFalse(updated_user_info['is_verified'])
        self.assertEqual(updated_user_info['owner_name'], user_info_used['owner_name'])

        updated_extra_info = updated_user_info['extra_info']
        extra_info_used = user_info_used['extra_info']

        self.assertEqual(updated_extra_info['uid'], updated_user_info['uid'])

        is_creation_date_correct = self.is_correct_creation_date(updated_user_info['extra_info']['creation_date'])
        self.assertTrue(is_creation_date_correct)
        self.assertEqual(updated_extra_info['creator_machine'], extra_info_used['creator_machine'])

    def assertUserInfoExistsInDb(self, updated_user_info):
        user_record = auth.get_user(updated_user_info['uid'])

        self.assertTrue(user_record)

        extra_user_info_founds = db.collection('test_extra_user_info').where('uid', '==', updated_user_info['uid']).get()
        extra_user_info_exists = len(extra_user_info_founds) >= 1
        self.assertTrue(extra_user_info_exists)
    
    def assertUserInfoHasValidInitTokenInformationInDb(self, updated_user_info):
        token_information_dicts = db.collection('test_token_information').where('user_info_id', '==', updated_user_info['uid']).get()
        exists_token_information = len(token_information_dicts) >= 1

        self.assertTrue(exists_token_information)

        if not exists_token_information:
            return None

        self.assertEqual(token_information_dicts[0].get('amount_of_tokens'), app_constants.get_init_tokens_on_signUp())

    #endregion

#*-*-*-*-*-*-*-*-*-*-*-*- tests *-*-*-*-*-*-*-*-*-*-*-*-*-*#

    def test_given_wrong_slfs_then_return_bad_request(self):
        #arrange
        request_body = helper.process_and_add_slfs({
            'user_info': faker_user_info_data.generate_good_user_info()
        })
        request_body['slfs'] = 'wrong_slfs'

        #act
        r = self.flask_test_client.post('/accounts/', json=request_body)

        #assert
        self.assertEqual(r.status_code, 400)

    def test_given_valid_user_info_then_signUp_correct_in_db(self):
        #arrange
        valid_user_info = faker_user_info_data.generate_good_user_info(1)
        request_body = helper.process_and_add_slfs({
            'user_info': valid_user_info
        })

        #act
        r = self.flask_test_client.post('/accounts/', json=request_body)

        #assert
        updated_user_info = r.json['updated_user_info']

        self.assertEqual(r.status_code, 201)
        self.assertGoodUpdatedUserInfo(updated_user_info, valid_user_info)
        self.assertUserInfoExistsInDb(updated_user_info)
        self.assertUserInfoHasValidInitTokenInformationInDb(updated_user_info)

    def test_given_invalid_user_info_then_error_code_is_INVALID_USERINFO(self):
        #arrange
        invalid_user_info = faker_user_info_data.generate_good_user_info()
        
        del invalid_user_info['password']

        request_body = helper.process_and_add_slfs({
            'user_info': invalid_user_info
        })

        #act
        r = self.flask_test_client.post('/accounts/', json=request_body)

        #assert
        error_code = r.json['error_code']

        self.assertEqual(r.status_code, 400)
        self.assertEqual(error_code, app_error_code.INVALID_USERINFO)

    def test_given_email_conflict_then_error_code_is_EMAIL_CONFLICT(self):
        #arrange
        request_body = helper.process_and_add_slfs({'user_info': faker_user_info_data.generate_good_user_info(email_number=2)})

        #act
        self.flask_test_client.post('/accounts/', json=request_body)
        r = self.flask_test_client.post('/accounts/', json=request_body)

        #assert
        error_code = r.json['error_code']

        self.assertEqual(error_code, app_error_code.EMAIL_CONFLICT)

    def test_given_too_many_signUp_then_error_code_is_TOO_MANY_SIGN_UP(self):
        #arrange and act
        r = None

        for i in range(1, app_constants.get_max_signUp_per_machine_in_range()+2):
            request_body = helper.process_and_add_slfs({
                'user_info': faker_user_info_data.generate_good_user_info(i)
            })

            r = self.flask_test_client.post('/accounts/', json=request_body)

        #assert
        error_code = r.json['error_code']

        self.assertEqual(r.status_code, 429)
        self.assertEqual(error_code, app_error_code.TOO_MANY_SIGN_UP)

    def test_given_extra_force_fields_then_ignore_it(self):
        #arrange
        user_info_to_signUp = faker_user_info_data.generate_good_user_info(1)

        user_info_to_signUp['is_verified'] = True
        user_info_to_signUp['uid'] = 'force_id'

        request_body = helper.process_and_add_slfs({
            'user_info': user_info_to_signUp
        })

        #act
        r = self.flask_test_client.post('/accounts/', json=request_body)

        #assert
        updated_user_info = r.json['updated_user_info']

        self.assertFalse(updated_user_info['is_verified'])
        self.assertNotEqual(updated_user_info['uid'], user_info_to_signUp['uid'])

#-*-*-*-*-*-*-*-*-*-* end tests -*-*-*-*-*-*-*-*-*-*-*-*-*#

if __name__ == '__main__':
    sys.argv.pop()
    unittest.main()