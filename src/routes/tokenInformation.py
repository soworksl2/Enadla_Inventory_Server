import json

import jwt
from flask import Blueprint, request, Response

import secretsKeys
from database.dbOperations import dbTokenInformationOperations
from helpers import serialization

tokenInformationBlueprint = Blueprint('tokenInformation', __name__)

@tokenInformationBlueprint.route('/', methods=['GET'])
def getTokenInformation():
    rawJWT = request.headers.get('auth')
    jwtDecoded = None
    isValidJWT = False

    try:
        jwtDecoded = jwt.decode(rawJWT, key=secretsKeys.jwtKeySecret, algorithms=['HS256'])
        isValidJWT = True
    except Exception as e:
        isValidJWT = False

    if not isValidJWT:
        responseBody = {
            'serverInformation': 'The JWT is not valid or does not exist'
        }
        return Response(status=401, response=json.dumps(responseBody))
    
    #here the JWT is valid
    currentTokenInformation = dbTokenInformationOperations.getTokenInformationByIdAccount(jwtDecoded['uid'])
    
    if currentTokenInformation == None:
        bodyResponse = {
            'serverInformation': 'the tokenInformation for the account was not found'
        }
        return Response(status=404, response=json.dumps(bodyResponse))

    return Response(status=200, response=json.dumps(currentTokenInformation.__dict__, default=serialization.defaultDump))