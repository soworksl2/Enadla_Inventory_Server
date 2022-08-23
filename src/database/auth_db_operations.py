from sys import argv
from datetime import datetime, timedelta

import pytz

import app_error_code
import app_constants
from own_firebase_admin import auth, db
from models import user_info
from database import token_information_operations

#region Collection Names as CN
is_debug = 'DEBUG' in argv

CN_EXTRA_USER_INFO = 'extra_user_info' if not is_debug else 'test_extra_user_info'
#endregion

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
