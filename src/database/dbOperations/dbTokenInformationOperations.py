from sys import argv
from datetime import datetime

import pytz
from firebaseAdmin import db
from models import TokenInformation

isDebug = 'DEBUG' in argv

#Collections names
tokenInformationCollectionName = 'tokenInformation' if not isDebug else 'tokenInformation-dev'
#*-*--**-*-*-*--**--*

def getTokenInformationByIdAccount(idAccount):
    tokenInformationFounds = db.collection(tokenInformationCollectionName).where('accountId', '==', idAccount).get()

    if len(tokenInformationFounds) <= 0:
        return None

    return TokenInformation.TokenInformation(**tokenInformationFounds[0].to_dict())

def addFreeTokensByIdAccount(idAccount, amountToAdd, maxFreeTokensLimit):
    if not amountToAdd >= 0:
        raise ValueError(f'amountToAdd should be equals or greather than 0 and you pass to in "{idAccount}"')
    if not maxFreeTokensLimit > 0:
        raise ValueError(f'maxFreeTokensLimit should be greather than 0 and you pass to in "{maxFreeTokensLimit}"')

    tokenInformationFounds = db.collection(tokenInformationCollectionName).where('accountId', '==', idAccount).get()

    if len(tokenInformationFounds) <= 0:
        raise Exception('the tokenInformation with the respectively idAccount was not found')

    currentTokenInformationSnapshot = tokenInformationFounds[0]
    currentFreeTokensCache = currentTokenInformationSnapshot.get('freeTokens')

    updatedFreeTokens = currentFreeTokensCache + amountToAdd
    if updatedFreeTokens > maxFreeTokensLimit:
        updatedFreeTokens = maxFreeTokensLimit
    
    currentTokenInformationSnapshot.reference.update({
        'freeTokens': updatedFreeTokens,
        'lastChargeFreeTokens': datetime.now(tz=pytz.UTC)
    })

    return updatedFreeTokens - currentFreeTokensCache