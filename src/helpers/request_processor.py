from flask import request
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

def parse_request(specification, field_converter = None):
    if request.is_json:
        valid_request = normalize_and_validate(specification, request.json)
    else:
        return None

    if not field_converter or not valid_request:
        return valid_request

    if not isinstance(field_converter, dict):
        raise TypeError('field_converter should be a dictionary')

    for key, value in field_converter.items():
        str_paths = [path.strip() for path in key.split('.')]

        if not all(str_paths):
            continue

        nested_dict: dict = valid_request
        for i in range(0, len(str_paths)):
            if not str_paths[i] in nested_dict:
                break

            if i == len(str_paths) - 1:
                if str_paths[i].endswith('**'):
                    nested_dict[str_paths[i]] = value(**nested_dict[str_paths[i]])
                else:
                    nested_dict[str_paths[i]] = value(nested_dict[str_paths[i]])
            else:
                nested_dict = nested_dict[str_paths[i]]
    
    return valid_request