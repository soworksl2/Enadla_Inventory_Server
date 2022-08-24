from datetime import datetime
import os
import sys
import unittest

import pytz

#region adding the project path to the sys.path
directory = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(os.path.dirname(directory))
parent = os.path.dirname(parent)
sys.path.append(parent)
#endregion

from helpers import own_response_factory, own_json

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class TestOwnResponseFactory(unittest.TestCase):

    #testing create_json_body as cjb

    def test_cjb_given_valid_parameters_then_mimetype_is_json(self):
        #arrange and act
        result = own_response_factory.create_json_body(200)

        #assert
        self.assertEqual(result.mimetype, 'application/json')

    #TODO: bad test
    def test_cjb_given_extra_fields_then_include_it(self):
        #arrange
        keys_and_values = {
            'test': 'test',
            'date': 2,
            'point': True
        }

        for key, value in keys_and_values.items():
            with self.subTest(key=key, value=value):
                #act
                result = own_response_factory.create_json_body(200, **{key: value})

                #assert
                expected = {key: value}
                self.assertEqual(result.json, expected)

    def test_cjb_given_error_code_then_error_code_include_it(self):
        #arrange and act
        result = own_response_factory.create_json_body(200, error_code='hola')

        #assert
        expected = {'error_code': 'hola'}
        self.assertEqual(result.json, expected)

    #end testing

if __name__ == '__main__':
    unittest.main()