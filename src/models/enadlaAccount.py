from cerberus import Validator

class EnadlaAccount:
    
    def __init__(self, id = None, creationDate = None, creatorMachine = None, email = None,
     password = None, ownerName = None, currentMachine = None, lastChangeOfMachineDate = None) -> None:
        self.id = id
        self.creationDate = creationDate
        self.creatorMachine = creatorMachine
        self.email = email
        self.password = password
        self.ownerName = ownerName
        self.currentMachine = currentMachine
        self.lastChangeOfMachineDate = lastChangeOfMachineDate


    def getStrictDict(self, optionalsAttributes = []):
        output = {
            'email': self.email,
            'password': self.password,
            'ownerName': self.ownerName
        }

        if 'id' in optionalsAttributes:
            output['id'] = self.id
        
        return output

emailRegex = '^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

newAccountSchema = {
    "creatorMachine": {
        "type": "string",
        "required": True,
        "empty": False
    },
    "email": {
        'required': True,
        'type': 'string',
        'empty': False,
        'maxlength': 50,
        'regex': emailRegex
    },
    "password": {
        'required': True,
        'type': 'string',
        'empty': False
    },
    "ownerName": {
        'required': True,
        'type': 'string',
        'empty': False
    }
}

def validate(enadlaAccount: EnadlaAccount, schema):
    """Validate the object and return a tuple (Bool, Dict | None). 
    the dictionary represent the errors"""
    
    v = Validator(schema, allow_unknown=True)

    isValid = v.validate(enadlaAccount.__dict__)
    lastErrorsValidation = None if isValid else v.errors

    return (isValid, lastErrorsValidation)