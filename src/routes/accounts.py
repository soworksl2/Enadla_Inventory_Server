import json
from datetime import datetime, timedelta
from flask import Blueprint, request, Response
import jwt
from models import enadlaAccount
import secretsKeys
import pytz

from database import dbOperations


accountsBlueprint = Blueprint('accounts', __name__)


@accountsBlueprint.route('/', methods=['POST'])
def createAccount():
    desiredAccount = enadlaAccount.EnadlaAccount(**request.json)

    #Delete undesired fields
    desiredAccount.id = None
    desiredAccount.creationDate = datetime.now(tz=pytz.UTC)
    desiredAccount.currentMachine = None
    desiredAccount.lastChangeOfMachineDate = None

    validationResult = enadlaAccount.validate(desiredAccount, enadlaAccount.newAccountSchema)

    if not validationResult[0]:
        return Response(status=400, response=json.dumps(validationResult[1]))

    return dbOperations.saveNewAccount(desiredAccount)

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