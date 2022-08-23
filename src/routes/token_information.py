import json
import os
from datetime import datetime, timedelta

import pytz
from flask import Blueprint, request, Response

from database import token_information_operations
from helpers import serialization, JWT_manipulation

DAYS_INTERVAL_TO_RECHARGE = int(os.environ.get('DAYS_INTERVAL_TO_RECHARGE_FREE_TOKENS', '30')) #TODO: extract this const value to environ
FREE_TOKENS_LIMIT = int(os.environ.get('FREE_TOKENS_LIMIT', '2')) #TODO: extract this const value to environ
FREE_TOKENS_AMOUNT_PER_CHARGE = int(os.environ.get('FREE_TOKENS_AMOUNT_PER_CHARGE', 2)) #TODO: extract this const value to environ

TokenInformation_BP = Blueprint('TokenInformation', __name__)

@TokenInformation_BP.route('/', methods=['GET'])
def get_TokenInformation():
    raw_JWT = request.headers.get('auth')
    is_valid_JWT, JWT_decoded = JWT_manipulation.decode_JWT(raw_JWT)

    if not is_valid_JWT:
        body_response = {
            'server_information': 'The JWT is not valid or does not exist'
        }
        return Response(status=401, response=json.dumps(body_response))
    
    #here the JWT is valid
    current_TokenInformation = token_information_operations.get_token_information_by_id_account(JWT_decoded['uid'])
    
    if current_TokenInformation == None:
        body_response = {
            'server_information': 'the tokenInformation for the account was not found'
        }
        return Response(status=404, response=json.dumps(body_response))

    body_response = {
        'rules': {
            'days_interval_to_recharge_free_tokens': DAYS_INTERVAL_TO_RECHARGE,
            'free_tokens_limit': FREE_TOKENS_LIMIT
        },
        'token_information': current_TokenInformation.__dict__
    }
    return Response(status=200, response=json.dumps(body_response, default=serialization.default_dump))

@TokenInformation_BP.route('/get_free_tokens/', methods=['GET', 'POST'])
def recharge_free_tokens():
    raw_JWT = request.headers.get('auth')
    is_valid_JWT, JWT_decoded = JWT_manipulation.decode_JWT(raw_JWT)

    if not is_valid_JWT:
        body_response = {
            'server_information': 'the jwt is not valid or it does not exists'
        }
        return Response(status=401, response=json.dumps(body_response))

    current_TokenInformation = token_information_operations.get_token_information_by_id_account(JWT_decoded['uid'])
    
    recharge_available_date = current_TokenInformation.last_charge_free_tokens + timedelta(days=DAYS_INTERVAL_TO_RECHARGE)
    today_date = datetime.now(tz=pytz.UTC)

    if today_date < recharge_available_date:
        response_body = {
            'server_information': 'it is too soon to recharge'
        }
        
        current_response = Response(status=200, response=json.dumps(response_body))
        current_response.headers.add('modification', 0)
        return current_response

    tokens_modifications = token_information_operations.add_free_tokens_by_id_account(
        current_TokenInformation.account_id,
        FREE_TOKENS_AMOUNT_PER_CHARGE,
        FREE_TOKENS_LIMIT)
    current_response = Response(status=200)
    current_response.headers.add('modification', tokens_modifications)
    return current_response