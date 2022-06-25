from sys import argv

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