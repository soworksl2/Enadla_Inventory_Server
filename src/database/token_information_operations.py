from sys import argv
from datetime import datetime

import pytz

from own_firebase_admin import db
from models import token_information


#Collections names as CN
is_debug = 'DEBUG' in argv

CN_TOKEN_INFORMATION = 'token_information' if not is_debug else 'test_token_information'
#*-*--**-*-*-*--**--*

def __get_token_information_SnapShot_by_id(user_info_id):
    token_information_collection = db.collection(CN_TOKEN_INFORMATION)

    token_informations_ref = token_information_collection.where('user_info_id', '==', user_info_id).get()

    if(len(token_informations_ref) < 1):
        new_token_information = token_information.TokenInformation(user_info_id, 0, datetime.now(tz=pytz.utc))
        _, new_token_information_ref = token_information_collection.add(new_token_information.__dict__)
        return new_token_information_ref.get()
    
    return token_informations_ref[0]

def recharge_tokens(user_info_id, amount_to_recharge):
    if(amount_to_recharge < 0):
        raise ValueError('the amount_to_recharge shoul be greather or equals than 0')

    token_information_SnapShot = __get_token_information_SnapShot_by_id(user_info_id)
    current_amount_of_tokens = token_information_SnapShot.get('amount_of_tokens')
    updated_amount_of_tokens = current_amount_of_tokens + amount_to_recharge

    update_query = {
        'amount_of_tokens': updated_amount_of_tokens,
        'datetime_last_token_recharge': datetime.now(tz=pytz.utc)
    }

    token_information_SnapShot.reference.update(update_query)
