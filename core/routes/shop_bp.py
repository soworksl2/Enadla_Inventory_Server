from flask import Blueprint

from core import app_error_code
from core.helpers import request_processor, own_response_factory
from core.database import auth_db_operations, shop_operations

shop_bp = Blueprint('shop', __name__)

@shop_bp.route('/get_balance_status_key/', methods=['GET'])
def get_balance_status_key():
    
    request_specification = {
        'custom_id_token': {'type': 'string', 'required': True},
        'balance_key': {'type': 'string', 'required': True}
    }

    is_valid_request, valid_request = request_processor.parse_request(request_specification)

    if not is_valid_request:
        return own_response_factory.create_json_body(400, error_code=app_error_code.HTTP_BASIC_ERROR)

    custom_id_token = valid_request['custom_id_token']

    try:
        firebase_id_token, custom_id_token_claims = auth_db_operations.process_custom_id_token(custom_id_token)
    except app_error_code.InvalidCustomIdTokenException:
        return own_response_factory.create_json_body(400, error_code=app_error_code.INVALID_CUSTOM_ID_TOKEN)

    if not custom_id_token_claims['is_verified']:
        return own_response_factory.create_json_body(409, error_code=app_error_code.UNVERIFIED_USER)

    try:
        decoded_firebase_id_token = auth_db_operations.verify_firebase_id_token(firebase_id_token, True)
    except:
        return own_response_factory.create_json_body(400, error_code=app_error_code.INVALID_ID_TOKEN)

    current_user_id = decoded_firebase_id_token['uid']

    try:
        balance_status_key = shop_operations.buy_balance_status_key(current_user_id, valid_request['balance_key'])
    except app_error_code.InsufficientTokensException:
        return own_response_factory.create_json_body(409, error_code=app_error_code.INSUFFICIENT_TOKENS)
    except Exception as e:
        print(f'an error ocurred while cunsume the tokens the error: {e}')
        return own_response_factory.create_json_body(400, error_code=app_error_code.UNEXPECTED_ERROR)

    #TODO: return in the response the updated tokenInformation too. Jimy Aguasviva - 10 september 2022
    return own_response_factory.create_json_body(
        status=200,
        balance_status_key=balance_status_key
    )
