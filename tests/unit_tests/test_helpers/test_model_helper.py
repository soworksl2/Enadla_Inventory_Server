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

from helpers import model_helper

class _Point:
    def __init__(self, x, y, z=0):
        self.x = x
        self.y = y
        self.z = z

class TestModelHelper(unittest.TestCase):

    def get_good_parameters(self, x, y, z):
        return {
            'x': x,
            'y': y,
            'z': z
        }

    def assertPoint(self, point,  x, y, z):
        self.assertEqual(x, point.x)
        self.assertEqual(y, point.y)
        self.assertEqual(z, point.z)

    #testing create_obj funtion as co

    def test_co_given_correct_parameters_then_correct(self):
        #arrange
        parameters = self.get_good_parameters(10, 10, 10)

        #act
        result = model_helper.create_obj(_Point, **parameters)

        #assert
        self.assertPoint(result, 10,10,10)

    def test_co_given_less_parameters_then_error(self):
        #arrange
        parameters = self.get_good_parameters(10,10,10)
        del parameters['x']

        with self.assertRaises(Exception):
            # act and assert

            model_helper.create_obj(_Point, **parameters)

    def test_co_given_good_parameters_less_optional_then_correct(self):
        #arrange
        parameters = self.get_good_parameters(10, 10, 10)
        del parameters['z']

        #act
        result = model_helper.create_obj(_Point, **parameters)

        #assert
        self.assertPoint(result, 10, 10, 0)

    def test_co_given_extra_fields_without_ignore_extra_fields_then_error(self):
        #arrange
        parameters = self.get_good_parameters(10, 10, 10)
        parameters['extra'] = 10
        
        with self.assertRaises(Exception):
            #act and assert
            result = model_helper.create_obj(_Point, ignore_extra_fields=False, **parameters)

    def test_co_given_extra_fields_with_ignore_extra_fields_then_correct(self):
        # arrange
        parameters = self.get_good_parameters(10, 10, 10)
        parameters['extra'] = 10

        #act
        result = model_helper.create_obj(_Point, **parameters)

        #assert
        self.assertPoint(result, 10, 10, 10)

    #**-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-

if __name__ == '__main__':
    unittest.main()