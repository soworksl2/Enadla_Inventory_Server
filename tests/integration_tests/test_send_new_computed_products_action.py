import sys
import unittest

sys.argv.append('DEBUG')

from core import create_app
from core.own_firebase_admin import default_bucket

from core import app_constants, app_error_code
from tests.integration_tests.helper import clear_firebase_operations
from core.models import computed_products
from core.database import computed_products_operations
from core.helpers import own_json

class TestGetLasComputedProductsAction(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        clear_firebase_operations.clear_tests_from_auth_db()
        clear_firebase_operations.clear_tests_collecion_from_firestore()
        clear_firebase_operations.clear_tests_from_storage()

        app_server = create_app.create()

        app_server.config.update({
            "TESTING": True
        })
        cls.flask_test_client = app_server.test_client()

    def tearDown(self) -> None:
        clear_firebase_operations.clear_tests_from_auth_db()
        clear_firebase_operations.clear_tests_collecion_from_firestore()
        clear_firebase_operations.clear_tests_from_storage()

        return super().tearDown()

    def get_good_computed_product(self, name_for_product='test_product_name'):
        return computed_products.ComputedProducts(
            ['test_user_id'],
            ['ignored_product_test'],
            [computed_products.SingleComputedProduct(
                1,
                '3hdc7s',
                name_for_product,
                ['test_alias', 'test_alias2'],
                ['bad_spelling', 'bad_spelling2'],
                40.2
            )]
        )

    def get_content_from_storage(self, blob_name):
        current_blob = default_bucket.get_blob(blob_name)

        if current_blob is None:
            raise FileNotFoundError()

        return current_blob.download_as_bytes().decode('utf-8')

    #-*-*-*-*-*-*-*-*-*-*-*-*-*-*-* tests -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*
    #si el api admin key no existe bad request
    #si el api admin key no es valida error
    #si no existe el new_computed_products_ error
    #si todo es valido y no hay backup
    #si todo es valido y hay backup

    def test_given_no_api_admin_key_then_bad_request_error(self):
        #arrange
        request_body = {
            'new_computed_products': self.get_good_computed_product().__dict__
        }

        #act
        r = self.flask_test_client.post('/computed_products/', json=request_body)

        #assert
        self.assertEqual(r.status_code, 400)

        error_code = r.json['error_code']
        self.assertEqual(error_code, app_error_code.HTTP_BASIC_ERROR)

    def test_given_invalid_api_admin_key_then_invalid_api_admin_key_error(self):
        #arrange
        request_body = {
            'api_admin_key': 'wrong_api_admin_key',
            'new_computed_products': self.get_good_computed_product().__dict__
        }

        #act
        r = self.flask_test_client.post('/computed_products/', json=request_body)

        #assert
        self.assertEqual(r.status_code, 401)

        error_code = r.json['error_code']
        self.assertEqual(error_code, app_error_code.INVALID_API_ADMIN_KEY)

    def test_given_no_new_computed_products_then_bad_request_error(self):
        #arrange
        request_body = {
            'api_admin_key': app_constants.get_api_admin_key()
        }

        #act
        r = self.flask_test_client.post('/computed_products/', json=request_body)

        #assert
        self.assertEqual(r.status_code, 400)

        error_code = r.json['error_code']
        self.assertEqual(error_code, app_error_code.HTTP_BASIC_ERROR)

    def test_given_valid_new_computed_products_then_save_it(self):
        #arrange
        new_computed_products = self.get_good_computed_product()
        request_body = {
            'api_admin_key': app_constants.get_api_admin_key(),
            'new_computed_products': new_computed_products.__dict__
        }

        #act
        r = self.flask_test_client.post('/computed_products/', json=request_body)

        #assert
        self.assertEqual(r.status_code, 200)

        expected_save_computed_products = own_json.dumps(new_computed_products)
        save_computed_products = self.get_content_from_storage(computed_products_operations.FULL_COMPUTED_PRODUCTS_FILENAME)

        self.assertEqual(save_computed_products, expected_save_computed_products)

    def test_given_valid_new_computed_products_and_there_is_backup_already(self):
        #arrange
        backup_computed_products = self.get_good_computed_product('test_product_backup')

        computed_products_operations.push_new_computed_products(backup_computed_products)

        new_computed_products = self.get_good_computed_product('test_actual_product')
        request_body = {
            'api_admin_key': app_constants.get_api_admin_key(),
            'new_computed_products': new_computed_products.__dict__
        }

        #act
        r = self.flask_test_client.post('/computed_products/', json=request_body)

        #assert
        self.assertEqual(r.status_code, 200)

        save_computed_products = self.get_content_from_storage(computed_products_operations.FULL_COMPUTED_PRODUCTS_FILENAME)
        save_backup_computed_products = self.get_content_from_storage(computed_products_operations.FULL_BACKUP_COMPUTED_PRODUCTS_FILENAME)
        
        expected_save_computed_products = own_json.dumps(new_computed_products)
        expected_backup_computed_products = own_json.dumps(backup_computed_products)

        self.assertEqual(save_backup_computed_products, expected_backup_computed_products)
        self.assertEqual(save_computed_products, expected_save_computed_products)

    #-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

if __name__ == '__main__':
    sys.argv.pop()
    unittest.main()