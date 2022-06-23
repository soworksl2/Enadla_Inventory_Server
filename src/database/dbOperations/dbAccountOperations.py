from sys import argv
from datetime import datetime, timedelta

import pytz
from firebaseAdmin import db

from models import enadlaAccount, TokenInformation

isDebug = 'DEBUG' in argv

#Collections names
accountCollectionName = 'accounts' if not isDebug else 'accounts-dev'
tokenInformationCollectionName = 'tokenInformation' if not isDebug else 'tokenInformation-dev'
#*-*--**-*-*-*--**--*

def saveNewAccount(account : enadlaAccount.EnadlaAccount):
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

def emailAlreadyExists(email):
    similarEmailAccount = db.collection(accountCollectionName).where('email', '==', email).get()
    
    if len(similarEmailAccount) > 0:
        return True
    return False

def isMachineAvalibleToSignUp(machineId):
    MAX_ACCOUNTS = 2
    RANGE_DAYS = 15

    accountsInRange = 0
    upperLimitDateAccountsCreation = datetime.now(tz=pytz.UTC)
    lowerLimitDateAccountsCreation = upperLimitDateAccountsCreation - timedelta(days=RANGE_DAYS)

    allCurrentMachineAccounts = db.collection(accountCollectionName).where('creatorMachine', "==", machineId).stream()
    for accountDoc in allCurrentMachineAccounts:
        creationDate: datetime = accountDoc.get('creationDate')

        if creationDate > lowerLimitDateAccountsCreation and creationDate < upperLimitDateAccountsCreation:
            accountsInRange = accountsInRange + 1

        if accountsInRange >= MAX_ACCOUNTS:
            return False

        if creationDate > upperLimitDateAccountsCreation:
            break
    
    return True

def getAccountByEmail(email):
    if email == None:
        return None

    emails = db.collection(accountCollectionName).where('email', '==', email).get()

    if len(emails) <= 0:
        return None
    
    account = enadlaAccount.EnadlaAccount(**emails[0].to_dict())
    account.id = emails[0].id
    return account
