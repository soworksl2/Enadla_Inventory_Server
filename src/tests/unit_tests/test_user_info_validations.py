import os
import sys
import unittest

directory = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(os.path.dirname(directory))
sys.path.append(parent)

from models import user_info

class TestUserInfoValidations(unittest.TestCase):

    def get_good_user_info(self):
        return user_info.UserInfo(
            email = 'jimy.waner11@gmail.com',
            password = 'u89cu89cdu89cd89cd',
            owner_name = 'Jimy Aguasviva',
            extra_info = user_info.ExtraUserInfo(
                creator_machine = 'vu8989v89jwsj89j89cw89'
            )
        )

    def get_posibles_empty_strings(self):
        return ['', ' ', '   ', None]

    #testing signup ruleset as su

    def test_su_given_good_user_info_then_is_valid(self):
        #arrange
        user = self.get_good_user_info()

        #act
        result = user_info.validate(user, user_info.R_SIGNUP)

        #assert
        self.assertTrue(result[0])
        self.assertEqual(0, len(result[1]))

    def test_su_given_user_with_multiple_fails_then_multiple_fails_in_result(self):
        #arrange
        user = self.get_good_user_info()
        user.email = None
        user.password = ''
        
        #act
        result = user_info.validate(user, user_info.R_SIGNUP)

        #arrange
        self.assertFalse(result[0])
        self.assertIn(user_info.ValidationFails.empty_email, result[1])
        self.assertIn(user_info.ValidationFails.invalid_email, result[1])
        self.assertIn(user_info.ValidationFails.empty_password, result[1])

    def test_su_given_empty_email_then_empty_email_fail(self):

        for email in self.get_posibles_empty_strings():
            with self.subTest(email=email):
                # arrange
                user = self.get_good_user_info()
                user.email = email

                #act
                result = user_info.validate(user, user_info.R_SIGNUP)

                #assert
                self.assertFalse(result[0])
                self.assertIn(user_info.ValidationFails.empty_email, result[1])

    def test_su_given_invalid_email_then_invalid_email_fail(self):
        posibles_invalid_emmail = ['jimy.waner11', 'jimy.@gmail.com@']

        for email in posibles_invalid_emmail:
            with self.subTest(email=email):
                #arrange
                user = self.get_good_user_info()
                user.email = email

                #act
                result = user_info.validate(user, user_info.R_SIGNUP)

                #assert
                self.assertFalse(result[0])
                self.assertIn(user_info.ValidationFails.invalid_email, result[1])

    def test_su_given_empty_password_then_empty_password_fail(self):
        
        for password in self.get_posibles_empty_strings():
            with self.subTest(password=password):
                #arrange
                user = self.get_good_user_info()
                user.password = password

                #act
                result = user_info.validate(user, user_info.R_SIGNUP)

                #assert
                self.assertFalse(result[0])
                self.assertIn(user_info.ValidationFails.empty_password, result[1])

    def test_su_given_short_password_then_short_password_fail(self):
        #arrange
        user = self.get_good_user_info()
        user.password = '12345'

        #act
        result = user_info.validate(user, user_info.R_SIGNUP)

        #assert
        self.assertFalse(result[0])
        self.assertIn(user_info.ValidationFails.short_password, result[1])

    def test_su_given_empty_owner_name_then_empty_owner_name_fail(self):

        for owner_name in self.get_posibles_empty_strings():
            with self.subTest(owner_name= owner_name):
                #arrange
                user = self.get_good_user_info()
                user.owner_name = owner_name

                #act
                result = user_info.validate(user, user_info.R_SIGNUP)

                #assert
                self.assertFalse(result[0])
                self.assertIn(user_info.ValidationFails.empty_owner_name, result[1])

    def test_su_given_short_owner_name_then_short_owner_name_fail(self):
        
        #the min lengh for owner_name is 3 character

        posibles_short_owner_name = ['j', 'ji', ' j', '', ' ']

        for owner_name in posibles_short_owner_name:
            with self.subTest(owner_name=owner_name):
                #arrange
                user = self.get_good_user_info()
                user.owner_name = owner_name

                #act
                result = user_info.validate(user, user_info.R_SIGNUP)

                #assert
                self.assertFalse(result[0])
                self.assertIn(user_info.ValidationFails.short_owner_name, result[1])

    def test_su_given_long_owner_name_then_long_owner_name_fail(self):
        posibles_long_owner_name = [
            '012345678901234567890123456789012345678901234567891',
            '0123456789012345678901234567890123456789012345678912',
            '01234567890123456789012345678901234567890123456789123',
            '012345678901234567890123456789012345678901234567891234'
        ]

        for owner_name in posibles_long_owner_name:
            with self.subTest(owner_name=owner_name):
                #arrange
                user = self.get_good_user_info()
                user.owner_name = owner_name

                #act
                result = user_info.validate(user, user_info.R_SIGNUP)

                #assert
                self.assertFalse(result[0])
                self.assertIn(user_info.ValidationFails.long_owner_name, result[1])

    def test_su_given_empty_extra_info__creator_machine_then_empty_creator_machine_fail(self):
        
        for creator_machine in self.get_posibles_empty_strings():
            with self.subTest(creator_machine=creator_machine):
                #arrange
                user = self.get_good_user_info()
                user.extra_info.creator_machine = creator_machine

                #act
                result = user_info.validate(user, user_info.R_SIGNUP)

                #assert
                self.assertFalse(result[0])
                self.assertIn(user_info.ValidationFails.empty_creator_machine, result[1])


    #-----------------------

if __name__ == '__main__':
    unittest.main()