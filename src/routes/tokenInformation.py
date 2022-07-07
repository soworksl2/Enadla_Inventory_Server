import json
import os
from datetime import datetime, timedelta

import pytz
from flask import Blueprint, request, Response

from database.dbOperations import dbTokenInformationOperations
from helpers import serialization, JWTManipulation

DAYS_INTERVAL_TO_RECHARGE = int(os.environ.get('DAYS_INTERVAL_TO_RECHARGE_FREE_TOKENS', '30'))
FREE_TOKENS_LIMIT = int(os.environ.get('FREE_TOKENS_LIMIT', '2'))
FREE_TOKENS_AMOUNT_PER_CHARGE = int(os.environ.get('FREE_TOKENS_AMOUNT_PER_CHARGE', 2))

tokenInformationBlueprint = Blueprint('tokenInformation', __name__)

@tokenInformationBlueprint.route('/', methods=['GET'])
def getTokenInformation():
    rawJWT = request.headers.get('auth')
    isValidJWT, jwtDecoded = JWTManipulation.decodeJWT(rawJWT)

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

    bodyResponse = {
        'rules': {
            'daysIntervalToRechargeFreeTokens': DAYS_INTERVAL_TO_RECHARGE,
            'freeTokensLimit': FREE_TOKENS_LIMIT
        },
        'tokenInformation': currentTokenInformation.__dict__
    }
    return Response(status=200, response=json.dumps(bodyResponse, default=serialization.defaultDump))

@tokenInformationBlueprint.route('/getFreeTokens/', methods=['GET', 'POST'])
def rechargeFreeTokens():
    rawJWT = request.headers.get('auth')
    isValidJWT, JWTDecoded = JWTManipulation.decodeJWT(rawJWT)

    if not isValidJWT:
        bodyResponse = {
            'serverInformation': 'the jwt is not valid or it does not exists'
        }
        return Response(status=401, response=json.dumps(bodyResponse))

    currentTokenInformation = dbTokenInformationOperations.getTokenInformationByIdAccount(JWTDecoded['uid'])
    
    rechargeAvailableDate = currentTokenInformation.lastChargeFreeTokens + timedelta(days=DAYS_INTERVAL_TO_RECHARGE)
    todayDate = datetime.now(tz=pytz.UTC)

    print(f'{todayDate} - {currentTokenInformation.lastChargeFreeTokens} - {rechargeAvailableDate}')

    if todayDate < rechargeAvailableDate:
        responseBody = {
            'serverInformation': 'it is too soon to recharge'
        }
        
        currentResponse = Response(status=200, response=json.dumps(responseBody))
        currentResponse.headers.add('modification', 0)
        return currentResponse

    tokensModification = dbTokenInformationOperations.addFreeTokensByIdAccount(
        currentTokenInformation.accountId,
        FREE_TOKENS_AMOUNT_PER_CHARGE,
        FREE_TOKENS_LIMIT)
    currentResponse = Response(status=200)
    currentResponse.headers.add('modification', tokensModification)
    return currentResponse