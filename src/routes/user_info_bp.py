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

    return (True, user_info_to_signUp)

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