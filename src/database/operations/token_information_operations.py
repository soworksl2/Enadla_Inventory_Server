from sys import argv
from datetime import datetime

import pytz

from own_firebase_admin import db
from models import token_information

is_debug = 'DEBUG' in argv

#Collections names
TokenInformation_collection_name = 'tokenInformation' if not is_debug else 'tokenInformation-dev'
#*-*--**-*-*-*--**--*

def get_token_information_by_id_account(id_account):
    token_information_founds = db.collection(TokenInformation_collection_name).where('account_id', '==', id_account).get()

    if len(token_information_founds) <= 0:
        return None

    return token_information.TokenInformation(**token_information_founds[0].to_dict())

def add_free_tokens_by_id_account(id_account, amount_to_add, max_free_tokens_limit):
    if not amount_to_add >= 0:
        raise ValueError(f'amountToAdd should be equals or greather than 0 and you pass to in "{id_account}"')
    if not max_free_tokens_limit > 0:
        raise ValueError(f'maxFreeTokensLimit should be greather than 0 and you pass to in "{max_free_tokens_limit}"')

    TokenInformation_founds = db.collection(TokenInformation_collection_name).where('account_id', '==', id_account).get()

    if len(TokenInformation_founds) <= 0:
        raise Exception('the tokenInformation with the respectively id_account was not found')

    current_TokenInformation_snapshot = TokenInformation_founds[0]
    current_free_tokens_cache = current_TokenInformation_snapshot.get('free_tokens')

    updated_free_tokens = current_free_tokens_cache + amount_to_add
    if updated_free_tokens > max_free_tokens_limit:
        updated_free_tokens = max_free_tokens_limit
    
    current_TokenInformation_snapshot.reference.update({
        'free_tokens': updated_free_tokens,
        'last_charge_free_tokens': datetime.now(tz=pytz.UTC)
    })

    return updated_free_tokens - current_free_tokens_cache