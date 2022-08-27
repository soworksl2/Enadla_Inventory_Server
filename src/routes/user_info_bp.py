from flask import Blueprint, request

import app_error_code
from models import user_info
from helpers import own_json
from helpers import own_response_factory
from database import auth_db_operations

#region constant keys for the body requests or response that use this BluePrint
USER_INFO_KEY = 'user_info'
UPDATED_USER_INFO_KEY = 'updated_user_info'
#endregion

user_info_bp = Blueprint('accounts', __name__)

def __get_signUp_request_data():
    """get and returns all the data in a request signup formatted

    Returns:
        tuple[bool, UserInfo]: 
            [0] is a bool that indicate wheter the request is good formatted.\n
            [1] is a UserInfo to signup or None if something goes wrong
    """

    if not request.is_json:
        return (False, None)

    request_body: dict = request.get_json()
    user_info_to_signUp = request_body.get(USER_INFO_KEY, None)

    if user_info_to_signUp is None:
        return (False, None)

    user_info_to_signUp = user_info.UserInfo.from_dict(**own_json.process_json_obj(user_info_to_signUp))

    if len(user_info_to_signUp.password) < 6:
        return (False, None)

    return (True, user_info_to_signUp)

def __get_auth_credentials_request_data():
    """get and return all the data in a request auth formatted

    Returns:
        tuple[bool, str, str]:
            [0] if the request is valid\n
            [1] the email if is correct\n
            [2] the password if is correct
    """

    if not request.is_json:
        return (False, None, None)

    request_body: dict = request.get_json()

    email = request_body.get('email', None)
    password = request_body.get('password', None)

    if not email or not password:
        return (False, None, None)

    if len(password) < 6:
        return (False, None, None)
    
    return (True, email, password)

def __get_send_email_verifiation_request_data():
    """get and return all data in the request as send_email_verification formatted

    Returns:
        tuple[bool, str]:
            [0] a bool indicating if the request is valid\n
            [1] the custom_id_token from the request
    """

    if not request.is_json:
        return (False, None)

    request_body: dict = request.get_json()

    custom_id_token = request_body.get('custom_id_token', None)

    if not custom_id_token:
        return (False, None)

    return (True, custom_id_token)

@user_info_bp.route('/', methods=['POST'])
def sign_up():
    is_request_valid, user_info_to_signUp = __get_signUp_request_data()

    if not is_request_valid:
        return own_response_factory.create_json_body(
            status=400,
            error_code=app_error_code.HTTP_BASIC_ERROR
        )

    try:
        updated_user_info = auth_db_operations.save_new_user_info(user_info_to_signUp)
    
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

    is_valid_request, email, password = __get_auth_credentials_request_data()

    if not is_valid_request:
        return own_response_factory.create_json_body(400, error_code=app_error_code.HTTP_BASIC_ERROR)

    try:
        custom_id_token, refresh_token, current_user_info = auth_db_operations.authenticate_with_credentials(email, password)
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

    is_request_valid, custom_id_token = __get_send_email_verifiation_request_data()

    if not is_request_valid:
        return own_response_factory.create_json_body(400, error_code=app_error_code.HTTP_BASIC_ERROR)

    try:
        auth_db_operations.send_email_verification(custom_id_token)
    except app_error_code.InvalidCustomIdTokenException:
        return own_response_factory.create_json_body(status=400, error_code=app_error_code.INVALID_CUSTOM_ID_TOKEN)
    except app_error_code.InvalidIdTokenException:
        return own_response_factory.create_json_body(status=400, error_code=app_error_code.INVALID_ID_TOKEN)
    except app_error_code.UserNotExistsOrDisableException:
        return own_response_factory.create_json_body(status=409, error_code=app_error_code.USER_NOT_EXISTS_OR_DISABLE)
    except:
        return own_response_factory.create_json_body(status=400, error_code=app_error_code.UNEXPECTED_ERROR)

    return own_response_factory.create_json_body(status=200)
