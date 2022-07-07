import jwt

import secretsKeys

def decodeJWT(rawJWT):
    isValid = False
    JWTDecoded = None

    try:
        JWTDecoded = jwt.decode(rawJWT, key=secretsKeys.jwtKeySecret, algorithms=['HS256'])
        isValid = True
    except Exception:
        JWTDecoded = None
        isValid = False

    return (isValid, JWTDecoded)