from cerberus import Validator

lastErrorsValidation = None

class EnadlaAccount:
    
    def __init__(self, email = None, password = None, ownerName = None, id = None) -> None:
        self.email = email
        self.password = password
        self.ownerName = ownerName
        self.id = id

    def getStrictDict(self, optionalsAttributes = []):
        output = {
            'email': self.email,
            'password': self.password,
            'ownerName': self.ownerName
        }

        if 'id' in optionalsAttributes:
            output['id'] = self.id
        
        return output

def validate(enadlaAccount: EnadlaAccount):
    """Validate the object and return a tuple (Bool, Dict | None). 
    the dictionari represent the errors"""
    
    global lastErrorsValidation

    emailRegex = '^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    enadlaAccountSchema = {
    'email' : {
        'required': True,
        'type': 'string',
        'empty': False,
        'maxlength': 25,
        'regex': emailRegex
        },
    'password': {
        'required': True,
        'type': 'string',
        'empty': False,
    },
    'ownerName':{
        'required': True,
        'type': 'string',
        'empty': False
    },
    'id':{
        'type': 'string',
        'default': ''
    }
}
    
    v = Validator(enadlaAccountSchema)

    isValid = v.validate(enadlaAccount.getStrictDict())
    lastErrorsValidation = None if isValid else v.errors

    return isValid