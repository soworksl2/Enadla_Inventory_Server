from flask import request
from cerberus import Validator

from helpers import own_json

class _RequestValidator(Validator):
    pass

def normalize_and_validate(schema, request_dict):
    validator = _RequestValidator(schema)

    normalized_request = validator.normalized(request_dict)

    if validator.validate(normalized_request):
        return normalized_request
    else:
        return None

def __convert_fields_of_dict(dict_to_convert, fields_converter):
    
    if not fields_converter or not isinstance(fields_converter, dict):
        raise TypeError('fields_converter should be a dict')

    for key in fields_converter.keys():
        if not isinstance(key, str):
            raise TypeError('each key of fields_converter dict should be a string')

    for full_path, converter in fields_converter.items():
        specific_dict_location = dict_to_convert
        path_splitted = full_path.split('.')
        last_path_index = len(path_splitted) - 1

        for index, path in enumerate(path_splitted):
            if index == last_path_index:
                if path.endswith('**'):
                    path_without_last_asterisks = path[:-2]
                    specific_dict_location[path_without_last_asterisks] = converter(**specific_dict_location[path_without_last_asterisks])
                else:
                    specific_dict_location[path] = converter(specific_dict_location[path])
            else:
                specific_dict_location = specific_dict_location[path]

def parse_request(specification, fields_converter = None):
    if not request.is_json:
        return (False, None)
    
    valid_request = normalize_and_validate(specification, request.json)

    if not valid_request:
        return (False, None)

    valid_request = own_json.process_json_obj(valid_request)

    if fields_converter:
        __convert_fields_of_dict(valid_request, fields_converter)

    return valid_request