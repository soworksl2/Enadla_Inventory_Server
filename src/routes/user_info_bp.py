from flask import Blueprint, request

import requests

import app_error_code
import app_constants
from models import user_info
from helpers import own_json
from helpers import own_response_factory
from database import auth_db_operations
from own_firebase_admin import auth

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
    
    return (True, email, password)

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
    
    API_KEY = app_constants.get_web_api_key()

    is_valid_request, email, password = __get_auth_credentials_request_data()

    if not is_valid_request:
        return own_response_factory.create_json_body(400, error_code=app_error_code.HTTP_BASIC_ERROR)
    
    firebase_request_body = {
        'email': email,
        'password': password,
        'returnSecureToken': True
    }
    r = requests.post(url=f'https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}', json=firebase_request_body)
    print(API_KEY)
    if not r.status_code == 200:
        return own_response_factory.create_json_body(400, error_code=app_error_code.UNEXPECTED_ERROR)

    response_content =  r.json()

    current_user_info = auth_db_operations.get_user_info_by_email(email)

    uid_token = auth.create_custom_token(response_content['localId'], { 'verified': current_user_info.is_verified }).decode('utf-8')
    refresh_token = response_content['refreshToken']

    return own_response_factory.create_json_body(
        status=200,
        id_token=uid_token,
        refresh_token=refresh_token,
        user_info=current_user_info
    )