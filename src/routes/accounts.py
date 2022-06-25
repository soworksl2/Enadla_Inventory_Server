import json
from datetime import datetime, timedelta

import jwt
import pytz
from flask import Blueprint, request, Response

import secretsKeys
from models import enadlaAccount
from helpers import serialization
from database.dbOperations import dbAccountOperations

accountsBlueprint = Blueprint('accounts', __name__)

@accountsBlueprint.route('/', methods=['POST'])
def createAccount():
    desiredAccount = enadlaAccount.EnadlaAccount(**request.json)

    #Delete undesired fields and adding today date
    desiredAccount.id = None
    desiredAccount.currentMachine = None
    desiredAccount.lastChangeOfMachineDate = None
    desiredAccount.creationDate = datetime.now(tz=pytz.UTC)

    validationResult = enadlaAccount.validate(desiredAccount, enadlaAccount.newAccountSchema)

    if not validationResult[0]:
        bodyResponse = {
            'serverInformation': 'the account is not valid',
            'validationFails': validationResult[1]
        }
        return Response(status=400, response=json.dumps(bodyResponse))

    if dbAccountOperations.emailAlreadyExists(desiredAccount.email):
        bodyResponse = {
            'serverInformation': f'the email "{desiredAccount.email}" already exists'
        }
        return Response(status=409, response=json.dumps(bodyResponse))

    if not dbAccountOperations.isMachineAvalibleToSignUp(desiredAccount.creatorMachine):
        bodyResponse = {
            'serverInformation': 'the machine from where you are trying to register has many sign up'
        }
        return Response(status=429, response=json.dumps(bodyResponse))

    dbAccountOperations.saveNewAccount(desiredAccount)
    return Response(status=201)

@accountsBlueprint.route('/auth/', methods=['GET'])
def authenticateAccount():
    accountToAuthenticate = enadlaAccount.EnadlaAccount(**request.json)

    if accountToAuthenticate.email == None:
        responseBody = {
            'serverInformation': 'the email cannot be null'
        }
        return Response(status=400, response=json.dumps(responseBody))

    originalAccount = dbAccountOperations.getAccountByEmail(accountToAuthenticate.email)

    if originalAccount == None:
        responseBody = {
            'serverInformation': f'the email "{accountToAuthenticate.email}" does not exists'
        }
        return Response(status=404, response=json.dumps(responseBody))

    if originalAccount.password != accountToAuthenticate.password:
        responseBody = {
            'serverInformation': 'the password is incorrect',
            'updatedAccount': json.dumps(originalAccount.__dict__, default=serialization.defaultDump)
        }
        return Response(status=400, response=json.dumps(responseBody))

    #Here the authentication is correct
    
    responseBody = {
        'updatedAccount': json.dumps(originalAccount.__dict__, default=serialization.defaultDump)
    }

    currentJwt = jwt.encode({
        'uid': originalAccount.id,
        'exp': datetime.now(tz=pytz.UTC) + timedelta(hours=2)
    }, key=secretsKeys.jwtKeySecret)

    currentResponse = Response(status=200, response=json.dumps(responseBody))
    currentResponse.headers['auth'] = currentJwt

    return currentResponse