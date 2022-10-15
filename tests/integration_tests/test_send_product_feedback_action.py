import sys
import unittest

sys.argv.append('DEBUG')

from core import create_app
from core.own_firebase_admin import default_bucket

from core import app_constants, app_error_code
from tests.integration_tests import helper
from tests.integration_tests.helper import clear_firebase_operations, database_helper
from core.models import product_feedback
from core.database import feedback_operations
from core.helpers import own_json

class TestsSendProductFeedbackAction(unittest.TestCase):

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

    #-*-*-*-*-*-*-*-*-*-*-*-*-*-*-* tests -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*
    #si el slfs no existe *
    #si el slfs es invalido *
    #si se envia un product feedback entonces guardarlo *
    #si se envia varios products feedback entonces guardarlos *
    #si se envia un product feedback que ya existia entonces actualizarlo *
    #si se envia un product feedback que ya existia pero con diferente costo entonces actualizarlo *
    #si se envia un product feedback que ya existia pero con diferente feedbackers entonces actualizarlo

    def test_given_no_slfs_then_error_400(self):
        #arrange
        request_body = {
            'custom_id_token': 'custom_id_token',
            'individual_products_feedback': []
        }

        #act
        r = self.flask_test_client.post('/feedback/product/', json=request_body)

        #asserts
        self.assertEqual(r.status_code, 400)

        error_code = r.json['error_code']
        self.assertEqual(error_code, app_error_code.HTTP_BASIC_ERROR)

    def test_given_wrong_slfs_then_error_400(self):
        #arrange
        request_body = {
            'custom_id_token': 'custom_id_token',
            'individual_products_feedback': [],
            'lt': 'test_lt',
            'slfs': 'wrong_slfs'
        }

        #act
        r = self.flask_test_client.post('/feedback/product/', json=request_body)

        #asserts
        self.assertEqual(r.status_code, 400)

        error_code = r.json['error_code']
        self.assertEqual(error_code, app_error_code.HTTP_BASIC_ERROR)

    def test_given_valid_individual_product_feedback_then_save_it(self):
        #arrange
        database_helper.signUp(self.flask_test_client, force_is_verified=True)
        current_custom_id_token, _, current_user_info_dict = database_helper.authenticate(self.flask_test_client)
        current_individual_product_feedback = product_feedback.IndividualProductFeedback(
            name='test_product',
            cost=100.99,
            repetition=100
        )

        request_body = helper.process_and_add_slfs({
            'custom_id_token': current_custom_id_token,
            'individual_products_feedback': [current_individual_product_feedback]
        })

        #act
        r = self.flask_test_client.post('/feedback/product/', json=request_body)

        #assert
        self.assertEqual(r.status_code, 200)

        expected_products_feedback = [
            product_feedback.ProductFeedback(
                product_name=current_individual_product_feedback.name,
                all_costs=[
                    product_feedback.CostProductFeedback(
                        cost=current_individual_product_feedback.cost,
                        concurrency=current_individual_product_feedback.repetition,
                        feedbackers=[
                            product_feedback.ProductFeedbacker(
                                uid=current_user_info_dict['uid'],
                                concurrency=current_individual_product_feedback.repetition
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

    def test_given_multiple_valid_individual_product_feedback_then_save_it(self):
        #arrange
        database_helper.signUp(self.flask_test_client, force_is_verified=True)
        current_custom_id_token, _, current_user_info_dict = database_helper.authenticate(self.flask_test_client)
        current_individual_products_feedback = [
            product_feedback.IndividualProductFeedback(
            name='test_product1',
            cost=100.99,
            repetition=100
            ),
            product_feedback.IndividualProductFeedback(
            name='test_product2',
            cost=100.99,
            repetition=100
            )
        ]

        request_body = helper.process_and_add_slfs({
            'custom_id_token': current_custom_id_token,
            'individual_products_feedback': current_individual_products_feedback
        })

        #act
        r = self.flask_test_client.post('/feedback/product/', json=request_body)

        #assert
        self.assertEqual(r.status_code, 200)

        expected_products_feedback = [
            product_feedback.ProductFeedback(
                product_name=current_individual_products_feedback[0].name,
                all_costs=[
                    product_feedback.CostProductFeedback(
                        cost=current_individual_products_feedback[0].cost,
                        concurrency=current_individual_products_feedback[0].repetition,
                        feedbackers=[
                            product_feedback.ProductFeedbacker(
                                uid=current_user_info_dict['uid'],
                                concurrency=current_individual_products_feedback[0].repetition
                            )
                        ]
                    )
                ]
            ),
            product_feedback.ProductFeedback(
                product_name=current_individual_products_feedback[1].name,
                all_costs=[
                    product_feedback.CostProductFeedback(
                        cost=current_individual_products_feedback[1].cost,
                        concurrency=current_individual_products_feedback[1].repetition,
                        feedbackers=[
                            product_feedback.ProductFeedbacker(
                                uid=current_user_info_dict['uid'],
                                concurrency=current_individual_products_feedback[1].repetition
                            )
                        ]
                    )
                ]
            )
        ]
        expected_products_feedback_dumped = own_json.dumps(expected_products_feedback, sort_keys=True)

        saved_products_feedback = feedback_operations.get_all_products_feedback()
        saved_products_feedback.sort(key=lambda i: i.product_name)
        saved_products_feedback_dumped = own_json.dumps(saved_products_feedback, sort_keys=True)
        
        self.assertEqual(saved_products_feedback_dumped, expected_products_feedback_dumped)

    def test_given_valid_individual_product_that_already_exists_then_update_it(self):
        #arrange
        database_helper.signUp(self.flask_test_client, force_is_verified=True)
        custom_id_token, _, current_user_info = database_helper.authenticate(self.flask_test_client)

        already_saved_individual_product_feedback = product_feedback.IndividualProductFeedback(
            name='test_product1',
            cost=100.99,
            repetition=10
        )
        new_individual_product_feedback = product_feedback.IndividualProductFeedback(
            name='test_product1',
            cost=100.99,
            repetition=100
        )

        feedback_operations.add_individual_products_feedback(current_user_info['uid'], [already_saved_individual_product_feedback])

        request_body = helper.process_and_add_slfs({
            'custom_id_token': custom_id_token,
            'individual_products_feedback': [new_individual_product_feedback]
        })

        #act
        r = self.flask_test_client.post('/feedback/product/', json=request_body)

        #asserts
        self.assertEqual(r.status_code, 200)

        expected_individual_products_feedback = [
            product_feedback.ProductFeedback(
                product_name=already_saved_individual_product_feedback.name,
                all_costs=[
                    product_feedback.CostProductFeedback(
                        cost=already_saved_individual_product_feedback.cost,
                        concurrency=already_saved_individual_product_feedback.repetition + new_individual_product_feedback.repetition,
                        feedbackers=[
                            product_feedback.ProductFeedbacker(
                                uid=current_user_info['uid'],
                                concurrency=already_saved_individual_product_feedback.repetition + new_individual_product_feedback.repetition
                            )
                        ]
                    )
                ]
            )
        ]
        expected_individual_products_feedback_dumped = own_json.dumps(expected_individual_products_feedback, sort_keys=True)

        saved_individual_products_feedback = feedback_operations.get_all_products_feedback()
        saved_individual_products_feedback_dumped = own_json.dumps(saved_individual_products_feedback, True)

        self.assertEqual(saved_individual_products_feedback_dumped, expected_individual_products_feedback_dumped)
    
    def test_given_valid_individual_product_that_already_exists_with_diferent_cost_then_update_it(self):
        #arrange
        database_helper.signUp(self.flask_test_client, force_is_verified=True)
        custom_id_token, _, current_user_info = database_helper.authenticate(self.flask_test_client)

        already_saved_individual_product_feedback = product_feedback.IndividualProductFeedback(
            name='test_product1',
            cost=100.99,
            repetition=10
        )
        new_individual_product_feedback = product_feedback.IndividualProductFeedback(
            name='test_product1',
            cost=200,
            repetition=100
        )

        feedback_operations.add_individual_products_feedback(current_user_info['uid'], [already_saved_individual_product_feedback])

        request_body = helper.process_and_add_slfs({
            'custom_id_token': custom_id_token,
            'individual_products_feedback': [new_individual_product_feedback]
        })

        #act
        r = self.flask_test_client.post('/feedback/product/', json=request_body)

        #asserts
        self.assertEqual(r.status_code, 200)

        expected_individual_products_feedback = [
            product_feedback.ProductFeedback(
                product_name=already_saved_individual_product_feedback.name,
                all_costs=[
                    product_feedback.CostProductFeedback(
                        cost=already_saved_individual_product_feedback.cost,
                        concurrency=already_saved_individual_product_feedback.repetition,
                        feedbackers=[
                            product_feedback.ProductFeedbacker(
                                uid=current_user_info['uid'],
                                concurrency=already_saved_individual_product_feedback.repetition
                            )
                        ]
                    ),
                    product_feedback.CostProductFeedback(
                        cost=new_individual_product_feedback.cost,
                        concurrency=new_individual_product_feedback.repetition,
                        feedbackers=[
                            product_feedback.ProductFeedbacker(
                                uid=current_user_info['uid'],
                                concurrency=new_individual_product_feedback.repetition
                            )
                        ]
                    )
                ]
            )
        ]
        expected_individual_products_feedback[0].all_costs.sort(key=lambda i: i.cost)
        expected_individual_products_feedback_dumped = own_json.dumps(expected_individual_products_feedback, sort_keys=True)

        saved_individual_products_feedback = feedback_operations.get_all_products_feedback()
        saved_individual_products_feedback[0].all_costs.sort(key=lambda i: i.cost)
        saved_individual_products_feedback_dumped = own_json.dumps(saved_individual_products_feedback, True)

        self.assertEqual(saved_individual_products_feedback_dumped, expected_individual_products_feedback_dumped)
  
    def test_given_valid_individual_product_that_already_exists_with_diferent_feedbacker_then_update_it(self):
        #arrange
        database_helper.signUp(self.flask_test_client, force_is_verified=True)
        database_helper.signUp(self.flask_test_client, email_number=2, force_is_verified=True)
        custom_id_token, _, current_user_info = database_helper.authenticate(self.flask_test_client)
        custom_id_token2, _, current_user_info2 = database_helper.authenticate(self.flask_test_client, email_number=2, custom_machine_id='another machine')

        already_saved_individual_product_feedback = product_feedback.IndividualProductFeedback(
            name='test_product1',
            cost=100.99,
            repetition=10
        )
        new_individual_product_feedback = product_feedback.IndividualProductFeedback(
            name='test_product1',
            cost=100.99,
            repetition=100
        )

        feedback_operations.add_individual_products_feedback(current_user_info['uid'], [already_saved_individual_product_feedback])

        request_body = helper.process_and_add_slfs({
            'custom_id_token': custom_id_token2,
            'individual_products_feedback': [new_individual_product_feedback]
        })

        #act
        r = self.flask_test_client.post('/feedback/product/', json=request_body)

        #asserts
        self.assertEqual(r.status_code, 200)

        expected_individual_products_feedback = [
            product_feedback.ProductFeedback(
                product_name=already_saved_individual_product_feedback.name,
                all_costs=[
                    product_feedback.CostProductFeedback(
                        cost=already_saved_individual_product_feedback.cost,
                        concurrency=already_saved_individual_product_feedback.repetition + new_individual_product_feedback.repetition,
                        feedbackers=[
                            product_feedback.ProductFeedbacker(
                                uid=current_user_info['uid'],
                                concurrency=already_saved_individual_product_feedback.repetition
                            ),
                            product_feedback.ProductFeedbacker(
                                uid=current_user_info2['uid'],
                                concurrency=new_individual_product_feedback.repetition
                            )
                        ]
                    )
                ]
            )
        ]
        expected_individual_products_feedback[0].all_costs[0].feedbackers.sort(key=lambda i: i.uid)
        expected_individual_products_feedback_dumped = own_json.dumps(expected_individual_products_feedback, sort_keys=True)

        saved_individual_products_feedback = feedback_operations.get_all_products_feedback()
        saved_individual_products_feedback[0].all_costs[0].feedbackers.sort(key=lambda i: i.uid)
        saved_individual_products_feedback_dumped = own_json.dumps(saved_individual_products_feedback, True)

        self.assertEqual(saved_individual_products_feedback_dumped, expected_individual_products_feedback_dumped)

    def test_given_valid_individual_product_that_already_exists_with_diferent_cost_and_diferent_feedbacker(self):
        #arrange
        database_helper.signUp(self.flask_test_client, force_is_verified=True)
        database_helper.signUp(self.flask_test_client, email_number=2, force_is_verified=True)
        custom_id_token, _, current_user_info = database_helper.authenticate(self.flask_test_client)
        custom_id_token2, _, current_user_info2 = database_helper.authenticate(self.flask_test_client, email_number=2, custom_machine_id='another machine')

        already_saved_individual_product_feedback = product_feedback.IndividualProductFeedback(
            name='test_product1',
            cost=100.99,
            repetition=10
        )
        new_individual_product_feedback = product_feedback.IndividualProductFeedback(
            name='test_product1',
            cost=200,
            repetition=100
        )

        feedback_operations.add_individual_products_feedback(current_user_info['uid'], [already_saved_individual_product_feedback])

        request_body = helper.process_and_add_slfs({
            'custom_id_token': custom_id_token2,
            'individual_products_feedback': [new_individual_product_feedback]
        })

        #act
        r = self.flask_test_client.post('/feedback/product/', json=request_body)

        #asserts
        self.assertEqual(r.status_code, 200)

        expected_individual_products_feedback = [
            product_feedback.ProductFeedback(
                product_name=already_saved_individual_product_feedback.name,
                all_costs=[
                    product_feedback.CostProductFeedback(
                        cost=already_saved_individual_product_feedback.cost,
                        concurrency=already_saved_individual_product_feedback.repetition,
                        feedbackers=[
                            product_feedback.ProductFeedbacker(
                                uid=current_user_info['uid'],
                                concurrency=already_saved_individual_product_feedback.repetition
                            )
                        ]
                    ),
                    product_feedback.CostProductFeedback(
                        cost=new_individual_product_feedback.cost,
                        concurrency=new_individual_product_feedback.repetition,
                        feedbackers=[
                            product_feedback.ProductFeedbacker(
                                uid=current_user_info2['uid'],
                                concurrency=new_individual_product_feedback.repetition
                            )
                        ]
                    )
                ]
            )
        ]
        expected_individual_products_feedback[0].all_costs.sort(key=lambda i: i.cost)
        expected_individual_products_feedback_dumped = own_json.dumps(expected_individual_products_feedback, sort_keys=True)

        saved_individual_products_feedback = feedback_operations.get_all_products_feedback()
        saved_individual_products_feedback[0].all_costs.sort(key=lambda i: i.cost)
        saved_individual_products_feedback_dumped = own_json.dumps(saved_individual_products_feedback, True)

        self.assertEqual(saved_individual_products_feedback_dumped, expected_individual_products_feedback_dumped)
  

    #-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

if __name__ == '__main__':
    sys.argv.pop()
    unittest.main()