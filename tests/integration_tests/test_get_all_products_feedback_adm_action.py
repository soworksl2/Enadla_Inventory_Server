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
from own_firebase_admin import default_bucket

import app_error_code
import app_constants
from helper import clear_firebase_operations, database_helper
from models import product_feedback
from database import feedback_operations
from helpers import own_json

class TestGetAllProductsFeedbackAction(unittest.TestCase):

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

    def test_given_no_api_admin_key_then_error_400(self):
        #arrange
        request_body = {
        }

        #act
        r = self.flask_test_client.get('/feedback/product/', json=request_body)

        #asserts
        self.assertEqual(r.status_code, 400)
        
        error_code = r.json['error_code']
        self.assertEqual(error_code, app_error_code.HTTP_BASIC_ERROR)

    def test_given_wrong_api_admin_key_then_error_INVALID_API_ADMIN_KEY(self):
        #arrange
        request_body={
            'api_admin_key': 'wrong_api_admin_key'
        }

        #act
        r = self.flask_test_client.get('/feedback/product/', json=request_body)

        #asserts
        self.assertEqual(r.status_code, 401)

        error_code = r.json['error_code']
        self.assertEqual(error_code, app_error_code.INVALID_API_ADMIN_KEY)

    def test_given_valid_request_with_no_products_feedback_saved_then_empty_list_returned(self):
        #arrange
        request_body={
            'api_admin_key': app_constants.get_api_admin_key()
        }

        #act
        r = self.flask_test_client.get('/feedback/product/', json=request_body)

        #asserts
        self.assertEqual(r.status_code, 200)

        expected_products_feedback = []
        expected_products_feedback_dumped = own_json.dumps(expected_products_feedback, sort_keys=True)
        saved_products_feedback = feedback_operations.get_all_products_feedback()
        saved_products_feedback_dumped = own_json.dumps(saved_products_feedback, sort_keys=True)

        self.assertEqual(saved_products_feedback_dumped, expected_products_feedback_dumped)

    def test_given_valid_request_with_products_feedback_saved_then_return_it(self):
        #arrange
        test_uid = 'some_test_uid'
        old_saved_products_feedback = [
            product_feedback.IndividualProductFeedback('product1', 100.99, 10),
            product_feedback.IndividualProductFeedback('product2', 25, 98)
        ]

        feedback_operations.add_individual_products_feedback(test_uid, old_saved_products_feedback)

        request_body={
            'api_admin_key': app_constants.get_api_admin_key()
        }

        #act
        r = self.flask_test_client.get('/feedback/product/', json=request_body)

        #asserts
        self.assertEqual(r.status_code, 200)

        expected_products_feedback = [
            product_feedback.ProductFeedback(
                old_saved_products_feedback[0].name,
                [
                    product_feedback.CostProductFeedback(
                        old_saved_products_feedback[0].cost,
                        old_saved_products_feedback[0].repetition,
                        [
                            product_feedback.ProductFeedbacker(
                                test_uid,
                                old_saved_products_feedback[0].repetition
                            )
                        ]
                    )
                ]
            ),
            product_feedback.ProductFeedback(
                old_saved_products_feedback[1].name,
                [
                    product_feedback.CostProductFeedback(
                        old_saved_products_feedback[1].cost,
                        old_saved_products_feedback[1].repetition,
                        [
                            product_feedback.ProductFeedbacker(
                                test_uid,
                                old_saved_products_feedback[1].repetition
                            )
                        ]
                    )
                ]
            )
        ]
        expected_products_feedback_dumped = own_json.dumps(expected_products_feedback, sort_keys=True)
        saved_products_feedback = feedback_operations.get_all_products_feedback()
        saved_products_feedback_dumped = own_json.dumps(saved_products_feedback, sort_keys=True)

        self.assertEqual(saved_products_feedback_dumped, expected_products_feedback_dumped)

    #-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

if __name__ == '__main__':
    sys.argv.pop()
    unittest.main()