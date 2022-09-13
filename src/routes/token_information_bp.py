from flask import Blueprint

import app_error_code
import app_constants
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

@token_information_bp.route('/recharge_by_uid_adm/', methods=['POST'])
def recharge_by_uid_adm():
    request_specification = {
        'api_admin_key': {'type': 'string', 'required': True},
        'uid': {'type': 'string', 'required': True},
        'amount': {'type': 'integer', 'required': True, 'min': 0}
    }

    is_valid_request, valid_request = request_processor.parse_request(request_specification, use_slfs=False)

    if not is_valid_request:
        return own_response_factory.create_json_body(400, error_code=app_error_code.HTTP_BASIC_ERROR)

    if not valid_request['api_admin_key'] == app_constants.get_api_admin_key():
        return own_response_factory.create_json_body(401, error_code=app_error_code.INVALID_API_ADMIN_KEY)

    try:
        token_information_operations.recharge_tokens(valid_request['uid'], valid_request['amount'])
    except app_error_code.UserNotExistsOrDisableException:
        return own_response_factory.create_json_body(404, error_code=app_error_code.USER_NOT_EXISTS_OR_DISABLE)
    except Exception:
        return own_response_factory.create_json_body(400, error_code=app_error_code.UNEXPECTED_ERROR)

    return own_response_factory.create_json_body(200)
