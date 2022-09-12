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

from helpers import balance_status_key_generators

class TestBalanceStatusKeyGenerator(unittest.TestCase):

    # testing generate balance status unlock key as gbusk

    def test_gbsuk_given_valid_balance_key_then_generate_valid_balance_status_unlock_key(self):
        #arrange
        valid_bk_and_bsuk = [
            (' ', '0;9e38fa18facf70622377fd48aebc4d17'),
            ('  ', '0;1d68648f0823e3cd39ef1ea0f0ba5372'),
            ('   ', '0;ed0bc1f6790ac5247b109f80ec087a20'),
            ('test balance key', '0;72258ff4d15448138f26bcf0ffd2dcaa'),
            ('330035e28262ec0c0addc7d332ad8ed8', '0;24332d39921ed53c63c0af1dd4deab94')]

        for valid_balance_key, valid_balance_status_unlock_key in valid_bk_and_bsuk:
            with self.subTest(balance_key=valid_balance_key, balance_status_unlock_key=valid_balance_status_unlock_key):
                #act
                result = balance_status_key_generators.generate_balance_status_unlock_key(valid_balance_key)

                #assert
                self.assertEqual(result, valid_balance_status_unlock_key)

    def test_gbsuk_given_empty_balance_key_then_ValueError(self):
        #arrange
        balance_key = ''

        with self.assertRaises(ValueError):
            #act and assert
            balance_status_key_generators.generate_balance_status_unlock_key(balance_key)

    # *-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-

if __name__ == '__main__':
    unittest.main()