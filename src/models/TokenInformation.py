
class TokenInformation:
    def __init__(self, accountId = None, freeTokens = 0, normalTokens = 0, lastChargeFreeToken = None) -> None:
        self.accountId = accountId
        self.freeTokens = freeTokens
        self.normalTokens = normalTokens
        self.lastChargeFreeTokens = lastChargeFreeToken

    def getStrictDict(self):
        return {
            'accountId': self.accountId,
            'freeTokens': self.freeTokens,
            'normalTokens': self.normalTokens,
            'lastChargeFreeTokens': self.lastChargeFreeTokens
        }