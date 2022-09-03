from flask import Blueprint

import app_error_code
from database import auth_db_operations, token_information_operations
from helpers import request_processor, own_response_factory

token_information_bp = Blueprint('token_information', __name__)

@token_information_bp.route('/', methods=['GET'])
def get_user_token_information():
    
    request_specification = {
        'custom_id_token': {'type': 'string', 'required': True}
    }

    is_valid_request, valid_request = request_processor.parse_request(request_specification)

    if not is_valid_request:
        return own_response_factory.create_json_body(400, error_code=app_error_code.HTTP_BASIC_ERROR)

    try:
        firebase_id_token, custom_id_token_claims = auth_db_operations.process_custom_id_token(valid_request['custom_id_token'])
    except app_error_code.InvalidCustomIdTokenException:
        return own_response_factory.create_json_body(400, error_code=app_error_code.INVALID_CUSTOM_ID_TOKEN)

    if not custom_id_token_claims['is_verified']:
        return own_response_factory.create_json_body(409, error_code=app_error_code.UNVERIFIED_USER)

    try:
        decoded_firebase_id_token = auth_db_operations.verify_firebase_id_token(firebase_id_token, True)
    except:
        return own_response_factory.create_json_body(400, error_code=app_error_code.INVALID_ID_TOKEN)

    current_user_id = decoded_firebase_id_token['uid']

    current_token_information = token_information_operations.get_token_information_by_id(current_user_id)

    return own_response_factory.create_json_body(
        status=200,
        token_information=current_token_information.get_client_dict()
    )