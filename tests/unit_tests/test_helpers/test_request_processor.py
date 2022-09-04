import os
import sys
import unittest

#region adding src folder to sys.path
root_path = os.path.dirname(os.path.realpath(__file__))
root_path = os.path.dirname(root_path)
root_path = os.path.dirname(root_path)
root_path = os.path.dirname(root_path)
src_path = os.path.join(root_path, 'src')
sys.path.append(src_path)
#endregion

from helpers import request_processor

class TestRequestProcessor(unittest.TestCase):

    # testing normalize and validate as nv

    def test_nv_given_valid_request_then_return_a_copy(self):
        #arrange
        request_sim_schema = {
            'name': {'type': 'string', 'required': True},
            'last_name': {'type': 'string', 'required': True}
        }

        request_sim = {
            'name': 'jimy',
            'last_name': 'Aguasviva'
        }

        #act
        result = request_processor.normalize_and_validate(request_sim_schema, request_sim)

        #assert
        expected = {
            'name': 'jimy',
            'last_name': 'Aguasviva'
        }
        self.assertEqual(result, expected)

    def test_nv_given_required_field_no_passed_then_no_valid(self):
       #arrange
        request_sim_schema = {
            'name': {'type': 'string', 'required': True},
            'last_name': {'type': 'string', 'required': True}
        }

        request_sim = {
            'name': 'jimy'
        } 

        #act
        result = request_processor.normalize_and_validate(request_sim_schema, request_sim)

        #assert
        self.assertIsNone(result)

    def test_nv_given_no_normalized_request_then_normalize_it(self):
        #arrange
        request_sim_schema = {
            'name': {'type': 'string', 'required': True},
            'last_name': {'type': 'string', 'default': ''}
        }

        request_sim = {
            'name': 'jimy'
        }

        #act
        result = request_processor.normalize_and_validate(request_sim_schema, request_sim)

        #assert
        expected = {
            'name': 'jimy',
            'last_name': ''
        }
        self.assertEqual(result, expected)

    # *-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-

if __name__ == '__main__':
    unittest.main()