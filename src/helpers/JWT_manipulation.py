import jwt

import secrets_keys

def decode_JWT(raw_JWT):
    is_valid = False
    JWT_decoded = None

    try:
        JWT_decoded = jwt.decode(raw_JWT, key=secrets_keys.jwt_key_secret, algorithms=['HS256'])
        is_valid = True
    except Exception:
        JWT_decoded = None
        is_valid = False

    return (is_valid, JWT_decoded)