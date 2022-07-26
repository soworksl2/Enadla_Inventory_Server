import unittest
import os
import sys

directory = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(os.path.dirname(directory))
sys.path.append(parent)

import app_constants

class _FakeEnvironContext:
    
    def __init__(self, fake_environ):
        self.fake_environ = fake_environ

    def __enter__(self):
        self.cache_environ = os.environ
        os.environ = self.fake_environ

    def __exit__(self, e_type, e_value, e_traceback):
        os.environ = self.fake_environ

class TestAppConstants(unittest.TestCase):

    def get_good_environ(self):
        good_environ = {
            "LAST_COMPATIBLE_CLIENT_VERSION": "1.0.0"
        }
        return good_environ

    def test_given_well_last_compatible_client_version_then_return_it(self):
        #arrange
        fake_environ = self.get_good_environ()
        fake_environ['LAST_COMPATIBLE_CLIENT_VERSION'] = '1.0.0'

        with _FakeEnvironContext(fake_environ):
            #act
            result = app_constants.get_last_compatible_client_version()

            #assert
            self.assertEqual((1, 0, 0), result)

    def test_given_undefined_client_version_then_get_last_compatible_client_version_raise_KeyError(self):
        # arrange
        fake_environ = self.get_good_environ()
        del fake_environ['LAST_COMPATIBLE_CLIENT_VERSION']

        with _FakeEnvironContext(fake_environ):
            #act and assert
            with self.assertRaises(KeyError):
                app_constants.get_last_compatible_client_version()

    def test_given_malformed_client_version_then_get_last_compatible_client_version_raise_ValueError(self):
        
        #arrange
        fake_environ = self.get_good_environ()
        
        malformed_version = ['1', '1.0', '1,0,0', 'mds', '1.2.m', 'm.m.m', '-1.0.0', '1.-1.0', '1.0.-1']

        for version in malformed_version:
            with self.subTest(version=version):
                fake_environ['LAST_COMPATIBLE_CLIENT_VERSION'] = version
                with _FakeEnvironContext(fake_environ):
                    with self.assertRaises(ValueError):
                        #act and assert
                        app_constants.get_last_compatible_client_version()

if __name__ == '__main__':
    unittest.main()