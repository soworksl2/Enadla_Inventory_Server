from cerberus import Validator

class _RequestValidator(Validator):
    pass

def normalize_and_validate(schema, request_dict):
    validator = _RequestValidator(schema)

    normalized_request = validator.normalized(request_dict)

    if validator.validate(normalized_request):
        return normalized_request
    else:
        return None