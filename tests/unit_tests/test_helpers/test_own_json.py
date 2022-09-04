import os
import sys
import unittest
import datetime

import pytz

#region adding src folder to sys.path
root_path = os.path.dirname(os.path.realpath(__file__))
root_path = os.path.dirname(root_path)
root_path = os.path.dirname(root_path)
root_path = os.path.dirname(root_path)
src_path = os.path.join(root_path, 'src')
sys.path.append(src_path)
#endregion

from helpers import own_json

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Wallet:
    def __init__(self, id, money):
        self.id = id
        self.money = money

class Person:
    def __init__(self, name, wallet):
        self.name = name
        self.wallet = wallet

class TestOwnJson(unittest.TestCase):
    
    # testing dumps as d

    def test_d_given_instance_dict_convertible_then_serialize(self):
        #arrange
        x = 10
        y = 12
        point = Point(x, y)

        #act
        serialized_point = own_json.dumps(point)

        #assert
        expected = f'{{"x": {x}, "y": {y}}}'
        self.assertEqual(serialized_point, expected)

    def test_d_given_dict_unconvertible_then_error(self):
        values_to_tests = [1, 1.0, "test", True, None]

        for value in values_to_tests:
            with self.subTest(value=value):
                with self.assertRaises(Exception):
                    #arrange and act and assert
                    serialized_obj = own_json.dumps(value)                

    def test_d_given_list_serializable_then_serialize(self):
        #arrange
        list_to_serialize = [0,1,2,3,4,5,6,7,8,9]

        #act
        serialized_list = own_json.dumps(list_to_serialize)

        #assert
        expected = '[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]'
        self.assertEqual(serialized_list, expected)

    def test_d_given_unserializable_value_in_dict_then_error(self):
        #arrange
        date_t = datetime.date(2000, 7, 29)
        x = {"unserializable_type": date_t}

        with self.assertRaises(Exception):
            #act and assert
            serialized_point = own_json.dumps(x)

    def test_d_given_unserializable_value_in_list_then_error(self):
        #arrange
        date_t = datetime.date(2000, 7, 29)
        x = [date_t]

        with self.assertRaises(Exception):
            #act and assert
            serialized_point = own_json.dumps(x)

    def test_d_given_datetime_value_then_serialize_it_with_project_format(self):
        #arrange
        datetime_value = datetime.datetime.now(tz=pytz.utc)
        obj = {"datetime": datetime_value}

        #act
        serialized = own_json.dumps(obj)

        #assert
        expected = f'{{"datetime": "{datetime_value.strftime("%Y-%m-%d %H:%M:%S %z")}"}}'
        self.assertEqual(serialized, expected)

    def test_d_given_datetime_without_timezoneInfo_then_valueError(self):
        #arrange
        datetime_value = datetime.datetime.now()
        obj = {"datetime": datetime_value}

        with self.assertRaises(ValueError):
            #act and assert
            serialized_obj = own_json.dumps(obj)

    def test_d_given_nested_obj_then_convert_to_dict_and_serialize_it(self):
        #arrange
        obj_to_dump = {
            'nested_obj': Point(10, 12)
        }

        #act
        dumped_obj = own_json.dumps(obj_to_dump)

        #assert
        expected = '{"nested_obj": {"x": 10, "y": 12}}'
        self.assertEqual(dumped_obj, expected)

    def test_d_given_composed_nested_obj_then_convert_to_dict_and_serialize_it(self):
        #arrange
        composed_obj = {
            'person': Person('test', Wallet('test', 100))
        }

        #act
        dumped_obj = own_json.dumps(composed_obj)

        #assert
        expected = '{"person": {"name": "test", "wallet": {"id": "test", "money": 100}}}'
        self.assertEqual(dumped_obj, expected)

    # *--***-*-*-*-*-

    #testing process_json_obj as pjo

    def test_pjo_given_not_a_dict_or_list_then_TypeError(self):
        #arrange
        obj_to_process = ['test', 1, 1.0, True, None, Point(10, 12)]

        for obj in obj_to_process:
            with self.subTest(obj=obj):
                with self.assertRaises(TypeError):
                    serialized_obj = own_json.process_json_obj(obj)

    def test_pjo_given_list_then_process_it(self):
        #arrange
        obj_to_process = [10, True, '2022-07-26 19:28:45 +0000']

        #act
        processed_obj = own_json.process_json_obj(obj_to_process)

        #assert
        expected = [10, True, datetime.datetime(2022, 7,26,19,28,45, tzinfo=pytz.utc)]
        self.assertEqual(processed_obj, expected)

    def test_pjo_given_dict_then_process_it(self):
        #arrange
        obj_to_process = {
            "name": "Jimy",
            "last_name": "Aguasviva",
            "is_married": False,
            "money_in_bank": 200.56,
            "birth_day": "2000-7-29 12:00:00 +0000"
        }

        #act
        processed_obj = own_json.process_json_obj(obj_to_process)

        #assert
        expected_obj = {
            "name": "Jimy",
            "last_name": "Aguasviva",
            "is_married": False,
            "money_in_bank": 200.56,
            "birth_day": datetime.datetime(2000, 7, 29, 12, 0, 0, tzinfo=pytz.utc)            
        }
        self.assertEqual(processed_obj, expected_obj)

    def test_pjo_given_recursivesly_list_then_process_it(self):
        #arrange
        date_to_use = '2000-7-29 19:11:11 +0000'
        list_to_process = [date_to_use, 'jimy', [date_to_use, 'jimy', [date_to_use, 'jimy'], [date_to_use, 'jimy']]]

        #act
        processed_obj = own_json.process_json_obj(list_to_process)

        #assert
        expected_date = datetime.datetime(2000, 7, 29, 19, 11, 11, tzinfo=pytz.utc)
        expected_list = [expected_date, 'jimy', [expected_date, 'jimy', [expected_date, 'jimy'], [expected_date, 'jimy']]]

        self.assertEqual(processed_obj, expected_list)

    def test_pjo_given_recursivesly_dict_then_process_it(self):
        #arrange
        datetime_to_use = '2000-7-29 19:11:11 +0000'
        obj_to_process = {
            'date': datetime_to_use,
            'name': 'Jimy',
            'last_name': {
                'date': datetime_to_use,
                'name': 'waner',
                'remains': [datetime_to_use, 'aguasviva', 'rodriguez']
            }
        }

        #act
        processed_obj = own_json.process_json_obj(obj_to_process)

        #assert
        expected_date = datetime.datetime(2000, 7, 29, 19, 11, 11, tzinfo=pytz.utc)
        expected_obj = {
            'date': expected_date,
            'name': 'Jimy',
            'last_name': {
                'date': expected_date,
                'name': 'waner',
                'remains': [expected_date, 'aguasviva', 'rodriguez']
            }
        }

        self.assertEqual(processed_obj, expected_obj)

    def test_pjo_given_basic_type_then_let_it_the_same(self):
        #arrange
        valid_types = [11, 11.5, 'hola', ['hola'], True, False, None]

        #act
        processed_obj = own_json.process_json_obj(valid_types)

        #assert
        self.assertEqual(processed_obj, valid_types)

    def test_pjo_given_valid_datetime_str_format_then_transform_value_to_datetime_type(self):
        #arrange
        obj_to_process = ['2022-07-26 19:28:45 +0000']

        #act
        processed_obj = own_json.process_json_obj(obj_to_process)

        #assert
        datetime_expected = datetime.datetime(2022, 7, 26, 19, 28, 45, tzinfo=pytz.utc)
        self.assertIsInstance(processed_obj[0], datetime.datetime)
        self.assertTrue(processed_obj[0].tzinfo is not None)
        self.assertEqual(processed_obj[0], datetime_expected)

    # *-*-*-*-*-*-**-***-*

    #testing loads as l

    def test_l_given_a_valid_serialized_obj_then_deserialize_it(self):
        #arrange
        serialized_obj = '{"name": "Jimy", "age": 22, "is_rich": false, "wallets": null, "cars": ["bike", "legs"]}'

        #act
        result = own_json.loads(serialized_obj)

        #assert
        expected = {
            'name': 'Jimy',
            'age': 22,
            'is_rich': False,
            'wallets': None,
            'cars': ['bike', 'legs']
        }
        self.assertEqual(result, expected)

    def test_l_given_some_value_with_specific_formatted_in_project_then_deserialize_it_correctly(self):
        #arrage
        serialized_obj = '{"date_now": "2022-07-26 19:28:45 +0000"}'

        #act
        result = own_json.loads(serialized_obj)

        #assert
        expected = {
            'date_now': datetime.datetime(2022, 7, 26, 19, 28, 45, tzinfo=pytz.utc)
        }
        self.assertEqual(result, expected)

    # *--**--*-*--**-*-*-*-

if __name__ == '__main__':
    unittest.main()