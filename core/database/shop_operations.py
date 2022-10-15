from core import app_constants
from core.database import token_information_operations
from core.helpers import balance_status_key_generators

def buy_balance_status_key(user_id, balance_key):
    balance_status_key_price = app_constants.get_balance_status_key_price()

    #if there are no sufficient tokens this will raise an exception that will be caught forwards
    token_information_operations.consume_tokens(user_id, balance_status_key_price)

    return balance_status_key_generators.generate_balance_status_unlock_key(balance_key)

