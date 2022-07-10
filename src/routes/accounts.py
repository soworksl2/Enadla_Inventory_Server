import json
from datetime import datetime, timedelta

import jwt
import pytz
from flask import Blueprint, request, Response

import secrets_keys
from models import enadla_account
from helpers import serialization
from database.operations import account_operations

accounts_BP = Blueprint('accounts', __name__)

@accounts_BP.route('/', methods=['POST'])
def create_account():
    desired_account = enadla_account.EnadlaAccount(**request.json)

    #Delete undesired fields and adding today date
    desired_account.id = None
    desired_account.current_machine = None
    desired_account.last_change_of_machine_date = None
    desired_account.creation_date = datetime.now(tz=pytz.UTC)

    validation_result = enadla_account.validate(desired_account, enadla_account.new_account_schema)

    if not validation_result[0]:
        body_response = {
            'server_information': 'the account is not valid',
            'validations_fails': validation_result[1]
        }
        return Response(status=400, response=json.dumps(body_response))

    if account_operations.email_already_exists(desired_account.email):
        body_response = {
            'server_information': f'the email "{desired_account.email}" already exists'
        }
        return Response(status=409, response=json.dumps(body_response))

    if not account_operations.is_machine_avalible_to_sign_up(desired_account.creator_machine):
        body_response = {
            'server_information': 'the machine from where you are trying to register has many sign up'
        }
        return Response(status=429, response=json.dumps(body_response))

    account_operations.save_new_account(desired_account)
    return Response(status=201)

@accounts_BP.route('/auth/', methods=['GET'])
def authenticate_account():
    account_to_authenticate = enadla_account.EnadlaAccount(**request.json)

    if account_to_authenticate.email == None:
        response_body = {
            'server_information': 'the email cannot be null'
        }
        return Response(status=400, response=json.dumps(response_body))

    original_account = account_operations.get_account_by_email(account_to_authenticate.email)

    if original_account == None:
        response_body = {
            'server_information': f'the email "{account_to_authenticate.email}" does not exists'
        }
        return Response(status=404, response=json.dumps(response_body))

    if original_account.password != account_to_authenticate.password:
        response_body = {
            'server_information': 'the password is incorrect',
            'updated_account': json.dumps(original_account.__dict__, default=serialization.default_dump)
        }
        return Response(status=400, response=json.dumps(response_body))

    #Here the authentication is correct
    
    response_body = {
        'updated_account': json.dumps(original_account.__dict__, default=serialization.default_dump)
    }

    current_JWT = jwt.encode({
        'uid': original_account.id,
        'exp': datetime.now(tz=pytz.UTC) + timedelta(hours=2)
    }, key=secrets_keys.jwt_key_secret)

    current_response = Response(status=200, response=json.dumps(response_body))
    current_response.headers['auth'] = current_JWT

    return current_response