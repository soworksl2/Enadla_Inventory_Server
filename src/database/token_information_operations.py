from sys import argv
from datetime import datetime

import pytz

import app_error_code
from own_firebase_admin import db
from models import token_information
from database import auth_db_operations


#Collections names as CN
is_debug = 'DEBUG' in argv

CN_TOKEN_INFORMATION = 'token_information' if not is_debug else 'test_token_information'
#*-*--**-*-*-*--**--*

def __get_token_information_SnapShot_by_id(user_info_id):
    if not auth_db_operations.exists_user_info_by_id(user_info_id):
        raise app_error_code.UserNotExistsOrDisableException()

    token_information_collection = db.collection(CN_TOKEN_INFORMATION)

    token_informations_ref = token_information_collection.where('user_info_id', '==', user_info_id).get()

    if(len(token_informations_ref) < 1):
        new_token_information = token_information.TokenInformation(user_info_id, 0, datetime.now(tz=pytz.utc))
        _, new_token_information_ref = token_information_collection.add(new_token_information.__dict__)
        return new_token_information_ref.get()
    
    return token_informations_ref[0]

def get_token_information_by_id(user_info_id):
    current_token_information_snapshot = __get_token_information_SnapShot_by_id(user_info_id)

    return token_information.TokenInformation(
        user_info_id=current_token_information_snapshot.get('user_info_id'),
        amount_of_tokens=current_token_information_snapshot.get('amount_of_tokens'),
        datetime_last_token_recharge=current_token_information_snapshot.get('datetime_last_token_recharge')
    )

def recharge_tokens(user_info_id, amount_to_recharge):
    if(amount_to_recharge < 0):
        raise ValueError('the amount_to_recharge should be greather or equals than 0')

    token_information_SnapShot = __get_token_information_SnapShot_by_id(user_info_id)
    current_amount_of_tokens = token_information_SnapShot.get('amount_of_tokens')
    updated_amount_of_tokens = current_amount_of_tokens + amount_to_recharge

    update_query = {
        'amount_of_tokens': updated_amount_of_tokens,
        'datetime_last_token_recharge': datetime.now(tz=pytz.utc)
    }

    token_information_SnapShot.reference.update(update_query)

def consume_tokens(user_info_id, amount_to_consume):
    """consume an amount of tokens from the db

    Args:
        user_info_id (str): the user id from where consume the tokens
        amount_to_consume (int): the amount of tokens to consume

    Raises:
        ValueError: if the amount to consume is minor than 0
        app_error_code.InsufficientTokensException: if there is not sufficient tokens in the account of an user
    """

    if amount_to_consume < 0:
        raise ValueError('the amount to consume should be greater or equals to 0')

    token_information_snapshot = __get_token_information_SnapShot_by_id(user_info_id)

    current_amount_of_tokens = token_information_snapshot.get('amount_of_tokens')

    if current_amount_of_tokens < amount_to_consume:
        raise app_error_code.InsufficientTokensException()

    updated_amount_of_tokens = current_amount_of_tokens - amount_to_consume

    update_query = {
        'amount_of_tokens': updated_amount_of_tokens
    }

    token_information_snapshot.reference.update(update_query)