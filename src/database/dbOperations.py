from sys import argv
from datetime import datetime

from flask import Response
from firebaseAdmin import db

from models import enadlaAccount, TokenInformation

isRelease = 'RELEASE' in argv

#Collections names
accountCollectionName = 'accounts' if isRelease else 'accounts-dev'
tokenInformationCollectionName = 'tokenInformation' if isRelease else 'tokenInformation-dev'
#*-*--**-*-*-*--**--*

def saveNewAccount(account: enadlaAccount.EnadlaAccount):
    
    conflictiveAccounts = db.collection(accountCollectionName).where('email', '==', account.email).get()
    if len(conflictiveAccounts) > 0:
        return Response('email already exists', status=409)

    batchOperation = db.batch()

    accountRef = db.collection(accountCollectionName).document()
    batchOperation.set(accountRef, account.getStrictDict())

    tokenInformationForNewUser = TokenInformation.TokenInformation(
        accountId=accountRef.id,
        freeTokens=2,
        lastChargeFreeToken=datetime.today())

    tokenInfoRef = db.collection(tokenInformationCollectionName).document()
    batchOperation.set(tokenInfoRef, tokenInformationForNewUser.getStrictDict())

    batchOperation.commit()

def confirmCredentials(accountCredential: enadlaAccount.EnadlaAccount):
    if not isinstance(accountCredential.email, str): 
        return {
            'succes': False,
            'response': Response('the email is invalid', status=400)
        }

    docsFound = db.collection(accountCollectionName).where('email', '==', accountCredential.email).get()

    if len(docsFound) <= 0:
        return {
            'succes': False,
            'response': Response('the email was no found', status=404)
        }

    credentialsAreValid = False

    passwordFound = docsFound[0].get('password')

    if passwordFound != accountCredential.password:
        return{
            'succes': False,
            'response': Response('the password is incorrect', status=400)
        }

    desiredAccount = enadlaAccount.EnadlaAccount(**docsFound[0].to_dict())
    desiredAccount.id = docsFound[0].id

    return {
        'succes': True,
        'response': desiredAccount
    }