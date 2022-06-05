from sys import argv
from datetime import datetime, timedelta

from flask import Response
import pytz
from firebaseAdmin import db

from models import enadlaAccount, TokenInformation

isDebug = 'DEBUG' in argv

#Collections names
accountCollectionName = 'accounts' if not isDebug else 'accounts-dev'
tokenInformationCollectionName = 'tokenInformation' if not isDebug else 'tokenInformation-dev'
#*-*--**-*-*-*--**--*

def saveNewAccount(account: enadlaAccount.EnadlaAccount):
    
    #check if email already exists
    similarEmailAccount = db.collection(accountCollectionName).where('email', '==', account.email).get()
    if len(similarEmailAccount) > 0:
        return Response('email already exists', status=409)

    #Check if the currentMachine has too many request
    MAX_ACCOUNTS = 2
    RANGE_DAYS = 15

    accountsInRange = 0
    upperLimitDateAccountsCreation = datetime.now(tz=pytz.UTC)
    lowerLimitDateAccountsCreation = upperLimitDateAccountsCreation - timedelta(days=RANGE_DAYS)

    allCurrentMachineAccounts = db.collection(accountCollectionName).where('creatorMachine', "==", account.creatorMachine).stream()
    for accountDoc in allCurrentMachineAccounts:
        creationDate: datetime = accountDoc.get('creationDate')

        if creationDate > lowerLimitDateAccountsCreation and creationDate < upperLimitDateAccountsCreation:
            accountsInRange = accountsInRange + 1

        if accountsInRange >= MAX_ACCOUNTS:
            return Response(status=429)

        if creationDate > upperLimitDateAccountsCreation:
            break

    # *--**-*--**-*--**-*-*-*-*-**-**-*-*-*-*-*-*-*-*-

    batchOperation = db.batch()

    accountRef = db.collection(accountCollectionName).document()
    batchOperation.set(accountRef, account.__dict__)

    tokenInformationForNewUser = TokenInformation.TokenInformation(
        accountId=accountRef.id,
        freeTokens=2,
        lastChargeFreeToken=datetime.now(tz=pytz.UTC))

    tokenInfoRef = db.collection(tokenInformationCollectionName).document()
    batchOperation.set(tokenInfoRef, tokenInformationForNewUser.__dict__)

    batchOperation.commit()
    return Response(status=201)

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