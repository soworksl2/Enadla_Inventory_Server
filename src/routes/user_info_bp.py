from flask import Blueprint, request, Response

import app_error_code
from models import user_info
from helpers import own_json
from database import auth_db_operations

#region constant keys for the body requests or response that use this BluePrint
USER_INFO_KEY = 'user_info'
UPDATED_USER_INFO_KEY = 'updated_user_info'
#endregion

user_info_bp = Blueprint('accounts', __name__)

@user_info_bp.route('/', methods=['POST'])
def sign_up():
    request_body = request.json
    user_info_to_signUp = own_json.process_json_obj(request_body[USER_INFO_KEY])
    user_info_to_signUp = user_info.UserInfo.from_dict(**user_info_to_signUp)

    try:
        updated_user_info = auth_db_operations.save_new_user_info(user_info_to_signUp)
    except app_error_code.InvalidUserinfoException:
        response_body = {
            'error_code': app_error_code.INVALID_USERINFO
        }
        return Response(status=400, response=own_json.dumps(response_body))
    except app_error_code.EmailConflictException:
        response_body = {
            'error_code': app_error_code.EMAIL_CONFLICT
        }
        return Response(status=409, response=own_json.dumps(response_body))
    except app_error_code.TooManySignUpException:
        response_body = {
            'error_code': app_error_code.TOO_MANY_SIGN_UP
        }
        return Response(status=429, response=own_json.dumps(response_body))

    response_body = {
        'updated_user_info': updated_user_info
    }
    return Response(status=201, response=own_json.dumps(response_body))