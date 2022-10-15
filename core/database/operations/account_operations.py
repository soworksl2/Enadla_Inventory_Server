from sys import argv
from datetime import datetime, timedelta

import pytz

from core.own_firebase_admin import db
from core.models import enadla_account, token_information

is_debug = 'DEBUG' in argv

#Collections names
account_collection_name = 'accounts' if not is_debug else 'accounts-dev'
token_information_collection_name = 'tokenInformation' if not is_debug else 'tokenInformation-dev'
#*-*--**-*-*-*--**--*

def save_new_account(account : enadla_account.EnadlaAccount):
    batch_operation = db.batch()

    account_ref = db.collection(account_collection_name).document()
    batch_operation.set(account_ref, account.__dict__)

    TokenInformation_for_new_user = token_information.TokenInformation(
        account_id=account_ref.id,
        free_tokens=2,
        last_charge_free_tokens=datetime.now(tz=pytz.UTC))

    token_info_ref = db.collection(token_information_collection_name).document()
    batch_operation.set(token_info_ref, TokenInformation_for_new_user.__dict__)

    batch_operation.commit()

def email_already_exists(email):
    similar_email_accounts = db.collection(account_collection_name).where('email', '==', email).get()
    
    if len(similar_email_accounts) > 0:
        return True
    return False

def is_machine_avalible_to_sign_up(machine_id):
    MAX_ACCOUNTS = 2 #TODO: extract this const to environ
    RANGE_DAYS = 15 #TODO: extract this const to environ

    accounts_in_range = 0
    upper_limit_date_accounts_creation = datetime.now(tz=pytz.UTC)
    lower_limit_date_accounts_creation = upper_limit_date_accounts_creation - timedelta(days=RANGE_DAYS)

    all_current_machine_accounts = db.collection(account_collection_name).where('creator_machine', "==", machine_id).stream()
    for account_snapshot in all_current_machine_accounts:
        creation_date = account_snapshot.get('creation_date')

        if creation_date > lower_limit_date_accounts_creation and creation_date < upper_limit_date_accounts_creation:
            accounts_in_range += 1

        if accounts_in_range >= MAX_ACCOUNTS:
            return False

        if creation_date > upper_limit_date_accounts_creation:
            break
    
    return True

def get_account_by_email(email):
    if email == None:
        return None

    emails = db.collection(account_collection_name).where('email', '==', email).get()

    if len(emails) <= 0:
        return None
    
    account = enadla_account.EnadlaAccount(**emails[0].to_dict())
    account.id = emails[0].id
    return account
