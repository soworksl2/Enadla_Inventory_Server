import sys
import os
import unittest
from datetime import datetime

import pytz

directory = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(os.path.dirname(directory))
sys.path.append(parent)

from models import enadla_account

class TestEnadlaAccountValidation(unittest.TestCase):

    def setUp(self):
        self.valid_EnadlaAccount = enadla_account.EnadlaAccount(
            id='3dg5fds93c',
            creation_date=datetime.now(tz=pytz.UTC),
            creator_machine='u89geg9g4u34uf4',
            email='jimy.waner11@gmail.com',
            password='df789f79f79h77c',
            owner_name='Jimy Aguasviva',
            current_machine='g9ff989uu89h3',
            last_change_of_machine_date=datetime.now(tz=pytz.UTC)
        )

        return super().setUp()

    def test_new_account_schema_given_valid_account_then_is_valid(self):
        #arrange

        #act
        result = enadla_account.validate(self.valid_EnadlaAccount, enadla_account.new_account_schema)

        #assert
        self.assertTrue(result[0])

    def test_new_account_schema_without_creator_machine_then_is_invalid(self):
        '''
        Given new account schema and correct enadla_account 
        without creator_machine then is invalid
        '''

        #arrange
        self.valid_EnadlaAccount.creator_machine = None
        
        #act
        validation_result = enadla_account.validate(self.valid_EnadlaAccount,
                                             enadla_account.new_account_schema)

        #assert
        self.assertFalse(validation_result[0])
        self.assertTrue('creator_machine' in validation_result[1].keys())

    def test_new_account_schema_without_email_then_is_invalid(self):

        possible_emails = ['', ' ', None] #TODO iterate in a subtests

        for email in possible_emails:
            with self.subTest(email=email):
                #arrange
                self.valid_EnadlaAccount.email = email
                
                #act
                result = enadla_account.validate(self.valid_EnadlaAccount, enadla_account.new_account_schema)

                #assert
                self.assertFalse(result[0])
                self.assertTrue('email' in result[1].keys())

    def test_new_account_schema_with_invalid_email_then_is_invalid(self):
        possibles_invalid_emails = ['jimy waner11@gmail.com', 'Jimy11']

        for email in possibles_invalid_emails:
            with self.subTest(email=email):
                #arrange
                self.valid_EnadlaAccount.email = email

                #act
                result = enadla_account.validate(self.valid_EnadlaAccount, enadla_account.new_account_schema)

                #assert
                self.assertFalse(result[0])
                self.assertTrue('email' in result[1].keys())

    def test_new_account_schema_without_password_then_is_invalid(self):
        possibles_empty_passwords = ['', ' ', None]

        for password in possibles_empty_passwords:
            with self.subTest(password=password):
                #arrange
                self.valid_EnadlaAccount.password = password

                #act
                result = enadla_account.validate(self.valid_EnadlaAccount, enadla_account.new_account_schema)

                #assert
                self.assertFalse(result[0])
                self.assertTrue('password' in result[1].keys())

    def test_new_account_schema_without_owner_name_then_is_invalid(self):
        possibles_empty_owner_name = ['', ' ', None]

        for owner_name in possibles_empty_owner_name:
            with self.subTest(owner_name=owner_name):
                #arrange
                self.valid_EnadlaAccount.owner_name = owner_name

                #act
                result = enadla_account.validate(self.valid_EnadlaAccount, enadla_account.new_account_schema)

                #assert
                self.assertFalse(result[0])
                self.assertTrue('owner_name' in result[1].keys())

if __name__ == '__main__':
    unittest.main()