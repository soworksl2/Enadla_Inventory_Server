import json
from datetime import datetime, timedelta
from flask import Blueprint, request, Response
import jwt
from models import enadlaAccount
import secretsKeys

from database import dbOperations


accountsBlueprint = Blueprint('accounts', __name__)


@accountsBlueprint.route('/', methods=['POST'])
def createAccount():
    desiredAccount = enadlaAccount.EnadlaAccount(**request.json)

    isValidAccount = enadlaAccount.validate(desiredAccount)

    if not isValidAccount:
        return Response(
            json.dumps(enadlaAccount.lastErrorsValidation),
            status=400,
            content_type='application/json'
            )


    resultOperation = dbOperations.saveNewAccount(desiredAccount)
    
    if resultOperation:
        return resultOperation   

    return Response(status=201)

@accountsBlueprint.route('/')
def logIn():
    credentialAccount = enadlaAccount.EnadlaAccount(**request.json)
    
    loginResult = dbOperations.confirmCredentials(credentialAccount)

    if not loginResult['succes']:
        return loginResult['response']
    
    accountFound = loginResult['response']

    currentToken = jwt.encode({'uid': accountFound.id, 'exp': datetime.now() + timedelta(days=1)}, secretsKeys.jwtKeySecret)

    res = Response(json.dumps(accountFound.getStrictDict(['id'])), status=200)
    res.headers['authorization'] = currentToken

    return res