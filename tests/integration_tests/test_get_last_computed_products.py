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

import app_error_code
from helper import clear_firebase_operations
from models import computed_products
from database import computed_products_operations
from helpers import own_json

class TestGetLasComputedProductsAction(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        clear_firebase_operations.clear_tests_from_auth_db()
        clear_firebase_operations.clear_tests_collecion_from_firestore()
        clear_firebase_operations.clear_tests_from_storage()

        app_server.config.update({
            "TESTING": True
        })
        cls.flask_test_client = app_server.test_client()

    def tearDown(self) -> None:
        clear_firebase_operations.clear_tests_from_auth_db()
        clear_firebase_operations.clear_tests_collecion_from_firestore()
        clear_firebase_operations.clear_tests_from_storage()

        return super().tearDown()

    #-*-*-*-*-*-*-*-*-*-*-*-*-*-*-* tests -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

    def test_given_no_computed_products_in_storage_then_error_code_404(self):
        #arrange and act
        r = self.flask_test_client.get('/computed_products/')

        #assert
        self.assertEqual(r.status_code, 404)

        error_code = r.json['error_code']
        self.assertEqual(error_code, app_error_code.HTTP_BASIC_ERROR)

    def test_given_one_compute_products_in_storage_then_return_it(self):
        #arrange
        current_computed_products = computed_products.ComputedProducts(
            ignored_users=['test_user_id'],
            ignored_products=['test_product'],
            products=[
                computed_products.SingleComputedProduct(
                    'test',
                    'xb9-gf679i-76t',
                    'test product',
                    ['alias1', 'alias2'],
                    ['bad_spelling1', 'bad_spelling2'],
                    409.5
                )
            ]
        )

        computed_products_operations.push_new_computed_products(current_computed_products)

        #act
        r = self.flask_test_client.get('/computed_products/')

        #assert
        self.assertEqual(r.status_code, 200)
        self.assertTrue('last_computed_products' in r.json)

        expected_last_computed_products = own_json.dumps(current_computed_products)
        expected_last_computed_products = own_json.loads(expected_last_computed_products)

        self.assertEqual(r.json['last_computed_products'], expected_last_computed_products)

    def test_given_multiple_computed_products_in_storage_then_return_the_last_one(self):
        #arrange
        first_computed_products = computed_products.ComputedProducts(
            ignored_users=['test_user_id'],
            ignored_products=['test_product'],
            products=[
                computed_products.SingleComputedProduct(
                    'test_1',
                    'xb9-gf679i-76t',
                    'test product',
                    ['alias1', 'alias2'],
                    ['bad_spelling1', 'bad_spelling2'],
                    409.5
                )
            ]
        )
        second_computed_products = computed_products.ComputedProducts(
            ignored_users=['test_user_id'],
            ignored_products=['test_product'],
            products=[
                computed_products.SingleComputedProduct(
                    'test_2',
                    'xb9-gf679i-76t',
                    'test product',
                    ['alias1', 'alias2'],
                    ['bad_spelling1', 'bad_spelling2'],
                    409.5
                )
            ]
        )

        computed_products_operations.push_new_computed_products(first_computed_products)
        computed_products_operations.push_new_computed_products(second_computed_products)

        #act
        r = self.flask_test_client.get('/computed_products/')

        #asserts
        self.assertEqual(r.status_code, 200)
        self.assertTrue('last_computed_products' in r.json)

        expected_last_computed_products = own_json.dumps(second_computed_products)
        expected_last_computed_products = own_json.loads(expected_last_computed_products)

        self.assertEqual(r.json['last_computed_products'], expected_last_computed_products)

    #-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

if __name__ == '__main__':
    sys.argv.pop()
    unittest.main()