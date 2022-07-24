from cerberus import Validator

class EnadlaAccount:
    
    def __init__(self, id = None, creation_date = None, creator_machine = None, email = None,
                 password = None, owner_name = None, current_machine = None,
                 last_change_of_machine_date = None):
        self.id = id
        self.creation_date = creation_date
        self.creator_machine = creator_machine
        self.email = email
        self.password = password
        self.owner_name = owner_name
        self.current_machine = current_machine
        self.last_change_of_machine_date = last_change_of_machine_date

def trim_all_fields_in_dict(dict_to_trim: dict):
    output = {}

    for key in dict_to_trim:
        if isinstance(dict_to_trim[key], str):
            output[key] = dict_to_trim[key].strip()
        elif isinstance(dict_to_trim[key], dict):
            output[key] = trim_all_fields_in_dict(dict_to_trim[key])
        else:
            output[key] = dict_to_trim[key]
    
    return output

def normalize(enadla_account: EnadlaAccount, schema = None):
    pass

email_regex = '^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

new_account_schema = {
    "creator_machine": {
        "type": "string",
        "required": True,
        "empty": False
    },
    "email": {
        'required': True,
        'type': 'string',
        'empty': False,
        'maxlength': 50,
        'regex': email_regex
    },
    "password": {
        'required': True,
        'type': 'string',
        'empty': False
    },
    "owner_name": {
        'required': True,
        'type': 'string',
        'empty': False
    }
}

def validate(enadla_account: EnadlaAccount, schema):
    """Validate the object and return a tuple (Bool, Dict | None). 
    the dictionary represent the errors"""
    
    v = Validator(schema, allow_unknown=True)

    account_dict = trim_all_fields_in_dict(enadla_account.__dict__)

    is_valid = v.validate(account_dict)
    last_errors_validation = None if is_valid else v.errors

    return (is_valid, last_errors_validation)