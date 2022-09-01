from flask import Blueprint

import app_error_code
from models import user_info
from helpers import request_processor, own_response_factory
from database import auth_db_operations

user_info_bp = Blueprint('accounts', __name__)

@user_info_bp.route('/', methods=['POST'])
def sign_up():
    request_specification = {
        'user_info': {'type': 'dict', 'required': True}
    }

    is_valid_request, valid_request = request_processor.parse_request(request_specification, {
        'user_info**': user_info.UserInfo.from_dict
    })

    if not is_valid_request:
        return own_response_factory.create_json_body(status=400, error_code=app_error_code.HTTP_BASIC_ERROR)

    try:
        updated_user_info = auth_db_operations.save_new_user_info(valid_request['user_info'])
    
    except app_error_code.InvalidUserinfoException:
        return own_response_factory.create_json_body(
            status=400,
            error_code=app_error_code.INVALID_USERINFO
        )
    
    except app_error_code.EmailConflictException:
        return own_response_factory.create_json_body(
            status=409,
            error_code=app_error_code.EMAIL_CONFLICT
        )
    
    except app_error_code.TooManySignUpException:
        return own_response_factory.create_json_body(
            status=429,
            error_code=app_error_code.TOO_MANY_SIGN_UP
        )
        
    return own_response_factory.create_json_body(
        status=201,
        updated_user_info=updated_user_info
    )

@user_info_bp.route('/auth/', methods=['GET'])
def authenticate_by_credentials():

    request_specification = {
        'email': {'type': 'string', 'required': True},
        'password': {'type': 'string', 'required': True, 'minlength': 6}
    }

    is_valid_request, valid_request = request_processor.parse_request(request_specification)

    if not is_valid_request:
        return own_response_factory.create_json_body(status=400, error_code=app_error_code.HTTP_BASIC_ERROR)

    try:
        custom_id_token, refresh_token, current_user_info = auth_db_operations.authenticate_with_credentials(valid_request['email'], valid_request['password'])
    except ValueError:
        return own_response_factory.create_json_body(400, error_code=app_error_code.HTTP_BASIC_ERROR)
    except app_error_code.InvalidCredentialsException:
        return own_response_factory.create_json_body(400, error_code=app_error_code.INVALID_CREDENTIALS)
    except app_error_code.UserNotExistsOrDisableException:
        return own_response_factory.create_json_body(409, error_code=app_error_code.USER_NOT_EXISTS_OR_DISABLE)
    except Exception as e:
        return own_response_factory.create_json_body(400, error_code=app_error_code.UNEXPECTED_ERROR)

    return own_response_factory.create_json_body(
        status=200,
        custom_id_token=custom_id_token,
        refresh_token=refresh_token,
        user_info=current_user_info
    )

@user_info_bp.route('/send_email_verification/', methods=['POST'])
def send_email_verification():

    request_specification = {
        'custom_id_token': {'type': 'string', 'required': True}
    }

    is_valid_request, valid_request = request_processor.parse_request(request_specification)

    if not is_valid_request:
        return own_response_factory.create_json_body(400, error_code=app_error_code.HTTP_BASIC_ERROR)

    try:
        auth_db_operations.send_email_verification(valid_request['custom_id_token'])
    except app_error_code.InvalidCustomIdTokenException:
        return own_response_factory.create_json_body(status=400, error_code=app_error_code.INVALID_CUSTOM_ID_TOKEN)
    except app_error_code.InvalidIdTokenException:
        return own_response_factory.create_json_body(status=400, error_code=app_error_code.INVALID_ID_TOKEN)
    except app_error_code.UserNotExistsOrDisableException:
        return own_response_factory.create_json_body(status=409, error_code=app_error_code.USER_NOT_EXISTS_OR_DISABLE)
    except:
        return own_response_factory.create_json_body(status=400, error_code=app_error_code.UNEXPECTED_ERROR)

    return own_response_factory.create_json_body(status=200)

@user_info_bp.route('/send_password_reset_email/', methods=['POST'])
def send_password_reset_email():
    
    request_specification = {
        'email': {'type': 'string', 'required': True}
    }

    is_valid_request, valid_request = request_processor.parse_request(request_specification)

    if not is_valid_request:
        return own_response_factory.create_json_body(status=400, error_code=app_error_code.HTTP_BASIC_ERROR)

    try:
        auth_db_operations.send_password_reset_email(valid_request['email'])
    except:
        return own_response_factory.create_json_body(400, error_code=app_error_code.UNEXPECTED_ERROR)

    return own_response_factory.create_json_body(status=200)
