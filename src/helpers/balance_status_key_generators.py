import hashlib

def generate_balance_status_unlock_key(balance_key):
    if not isinstance(balance_key, str):
        raise ValueError('the balance key should be string')

    if not balance_key:
        raise ValueError('the balance key should not be empty')

    unlock_code = '0'

    balance_status_unlock_key_raw = f'{unlock_code};{balance_key};enadla'

    md5_alg = hashlib.md5()
    md5_alg.update(balance_status_unlock_key_raw.encode('utf-8'))

    balance_status_unlock_key_processed = f'{unlock_code};{md5_alg.hexdigest()}'
    return balance_status_unlock_key_processed