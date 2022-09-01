from sys import argv
from datetime import datetime, timedelta

import pytz
import requests

import app_error_code
import app_constants
from own_firebase_admin import auth, db
from models import user_info
from database import token_information_operations
from helpers import own_json

#region Collection Names as CN
is_debug = 'DEBUG' in argv

CN_EXTRA_USER_INFO = 'extra_user_info' if not is_debug else 'test_extra_user_info'
#endregion

#TODO: extract API_WEB_KEY const from each method and make it a global const

def __has_machine_too_many_signUp(machine_id):
    RANGE_FOR_MAX_SIGNUP = app_constants.get_range_for_max_signUp()
    MAX_SIGNUP_PER_MACHINE = app_constants.get_max_signUp_per_machine_in_range()
    
    upper_limit_range = datetime.now(tz=pytz.utc)
    bottom_limit_range = upper_limit_range - timedelta(RANGE_FOR_MAX_SIGNUP)

    extra_user_info_collection = db.collection(CN_EXTRA_USER_INFO)
    all_extra_user_info_from_machine = extra_user_info_collection.where('creator_machine', '==', machine_id).stream()

    user_infos_in_limit_range = 0
    for extra_user_info in all_extra_user_info_from_machine:
        creation_date = extra_user_info.get('creation_date')

        if creation_date >= bottom_limit_range and creation_date <= upper_limit_range:
            user_infos_in_limit_range += 1

            if user_infos_in_limit_range >= MAX_SIGNUP_PER_MACHINE:
                break
    
    return user_infos_in_limit_range >= MAX_SIGNUP_PER_MACHINE

def does_email_exists(email: str):
    email_exists = True
    
    try:
        auth.get_user_by_email(email)
    except auth.UserNotFoundError:
        email_exists = False
    
    print(f'user was found: {email_exists}')

    return email_exists

def save_new_user_info(user_info_to_save: user_info.UserInfo):

    validation_result = user_info.validate(user_info_to_save, user_info.R_SIGNUP)

    if not validation_result[0]:
        raise app_error_code.InvalidUserinfoException()

    if does_email_exists(user_info_to_save.email):
        raise app_error_code.EmailConflictException()
    
    if __has_machine_too_many_signUp(user_info_to_save.extra_info.creator_machine):
        raise app_error_code.TooManySignUpException()

    updated_user_info_record = auth.create_user(
        display_name = user_info_to_save.owner_name,
        email = user_info_to_save.email,
        email_verified = False,
        password = user_info_to_save.password
    )

    updated_user_info = user_info.UserInfo(
        uid=updated_user_info_record.uid,
        email=user_info_to_save.email,
        password=None,
        is_verified=updated_user_info_record.email_verified,
        owner_name=updated_user_info_record.display_name,
        extra_info=user_info.ExtraUserInfo(
            uid=updated_user_info_record.uid,
            creation_date=datetime.now(tz=pytz.utc),
            creator_machine=user_info_to_save.extra_info.creator_machine
        )
    )

    extra_user_info_collection = db.collection(CN_EXTRA_USER_INFO)
    extra_user_info_collection.add(updated_user_info.extra_info.__dict__)

    INIT_TOKENS_ON_SIGNUP = app_constants.get_init_tokens_on_signUp()
    token_information_operations.recharge_tokens(updated_user_info.uid, INIT_TOKENS_ON_SIGNUP)

    return updated_user_info

def __get_extra_info(uid):
    extra_user_info_collection = db.collection(CN_EXTRA_USER_INFO)

    extra_user_info_founds = extra_user_info_collection.where('uid', '==', uid).get()

    if len(extra_user_info_founds) <= 0:
        raise Exception(f'the extra info for the uid was not found in the collection "{CN_EXTRA_USER_INFO}"')

    specific_extra_user_info = extra_user_info_founds[0]

    return user_info.ExtraUserInfo(
        uid=uid,
        creation_date=specific_extra_user_info.get('creation_date'),
        creator_machine=specific_extra_user_info.get('creator_machine')
    )

def get_user_info_by_email(email, add_extra_info = False):
    
    try:
        user_info_record = auth.get_user_by_email(email)
    except auth.UserNotFoundError:
        return None

    user_info_output = user_info.UserInfo(
        uid=user_info_record.uid,
        email=user_info_record.email,
        password=None,
        is_verified=user_info_record.email_verified,
        owner_name=user_info_record.display_name,
        extra_info= None if not add_extra_info else __get_extra_info(user_info_record.uid)
    )

    return user_info_output

def authenticate_with_credentials(email, password):
    """authenticate with email and password in the firebase identity api rest

    Args:
        email (str): a valid email
        password (str): a md5 hexadecimals formatted password

    Raises:
        ValueError: if the email or the password are empty or are null
        app_error_code.InvalidCredentialsException: if the email or password are incorrect
        app_error_code.UserNotExistsOrDisableException: if the user does not exists or is disable

    Returns:
        tuple[str, str, user_info.UserInfo]: \n
            [0] contains a dumped to str dictionary that contains {id_token-with the id token} and {custom_claims-dictionary with all custom claims of the id_token}
                the values of the custom_claims are:
                - is_verified: bool
            
            [1] contains a str that represent the refresh_token

            [2] the whole user_info for the current id_token
    """

    if not email or not password:
        raise ValueError('the email or the password cannot be empty or null')

    WEB_API_KEY = app_constants.get_web_api_key()

    url_sign_in_with_credentials_firebase = f'https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={WEB_API_KEY}'
    firebase_request_body = {
        'email': email,
        'password': password,
        'returnSecureToken': True
    }

    firebase_response = requests.post(url=url_sign_in_with_credentials_firebase, json=firebase_request_body)

    if not firebase_response.status_code == 200:
        firebase_error_message = None
        
        try:
            firebase_error_message = firebase_response.json()['error']['message']
        except:
            raise app_error_code.UnexpectedError()
        
        if firebase_error_message == 'EMAIL_NOT_FOUND' or firebase_error_message == 'INVALID_PASSWORD':
            raise app_error_code.InvalidCredentialsException()
        elif firebase_error_message == 'USER_DISABLED':
            raise app_error_code.UserNotExistsOrDisableException()
        else:
            raise app_error_code.UnexpectedError()

    response_body = firebase_response.json()

    id_token = response_body['idToken']
    refresh_token = response_body['refreshToken']
    current_user_info = get_user_info_by_email(email, add_extra_info=True)

    custom_id_token = own_json.dumps({
        'id_token': id_token,
        'custom_claims': {
            'is_verified': current_user_info.is_verified
        }
    })

    return (custom_id_token, refresh_token, current_user_info)

def process_custom_id_token(custom_id_token):
    """extract data from the custom_id_token

    Args:
        custom_id_token (str): the custom id token

    Raises:
        app_error_code.InvalidCustomIdTokenException: if the custom id token is invalid

    Returns:
        tuple[str, dict]: a tuple that contains
            [0] the id token\n
            [2] the custom claims for the specific id token 
    """

    if not custom_id_token:
        raise app_error_code.InvalidCustomIdTokenException()

    try:
        processed_custom_id_token = own_json.loads(custom_id_token)
    except:
        raise app_error_code.InvalidCustomIdTokenException()

    return (processed_custom_id_token['id_token'], processed_custom_id_token['custom_claims'])

def verify_firebase_id_token(firebase_id_token, check_revoked=False):
    """it is a wraper for the firebase auth.verify_id_token, see te documentation on firebase

    Args:
        firebase_id_token (str): the firebase_id_token
        check_revoked (bool, optional): if check revoked

    Returns:
        dict: the decoded token
    """

    return auth.verify_id_token(firebase_id_token, check_revoked=check_revoked)

def send_email_verification(custom_id_token):
    """send an email of verificaion to a user depending on the custom_id_token (this is an wrapper for the firebase api rest option)

    Args:
        custom_id_token (str): the custom id token

    Raises:
        app_error_code.InvalidCustomIdTokenException: if the custom id token is invalid
        app_error_code.UnexpectedError: if something unexpected goes wrong
        app_error_code.InvalidIdTokenException: if the id token is wrong
        app_error_code.UserNotExistsOrDisableException: if the user does not exists or is disable
    """ 

    API_WEB_KEY = app_constants.get_web_api_key()

    firebase_id_token, _ = process_custom_id_token(custom_id_token)

    firebase_url_api = f'https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={API_WEB_KEY}'
    firebase_request_body = {
        'requestType': 'VERIFY_EMAIL',
        'idToken': firebase_id_token
    }

    firebase_response =requests.post(url=firebase_url_api, json=firebase_request_body)

    if not firebase_response.status_code == 200:
        firebase_error_message = None
        
        try:
            firebase_error_message = firebase_response.json()['error']['message']
        except:
            raise app_error_code.UnexpectedError()

        if firebase_error_message == 'INVALID_ID_TOKEN':
            raise app_error_code.InvalidIdTokenException()
        elif firebase_error_message == 'USER_NOT_FOUND':
            raise app_error_code.UserNotExistsOrDisableException()
        else:
            raise app_error_code.UnexpectedError()

def send_password_reset_email(email):
    """send an email to recovery the password. (it is a wrapper of a endpoint firebase api)

    Args:
        email (str): the email to recovery the password

    Raises:
        app_error_code.UnexpectedError: something went wrong
        app_error_code.UserNotExistsOrDisableException: if the email was no found
    """

    API_WEB_KEY = app_constants.get_web_api_key()

    firebase_url_endPoint = f'https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={API_WEB_KEY}'
    firebase_request_body = {
        'requestType': 'PASSWORD_RESET',
        'email': email
    }

    firebase_response = requests.post(url=firebase_url_endPoint, json=firebase_request_body)

    if not firebase_response.status_code == 200:
        firebase_error_message = None
        
        try:
            firebase_error_message = firebase_response.json()['error']['message']
        except:
            raise app_error_code.UnexpectedError()

        if firebase_error_message == 'EMAIL_NOT_FOUND':
            raise app_error_code.UserNotExistsOrDisableException()
        else:
            raise app_error_code.UnexpectedError()

