import hashlib
import json
from multiprocessing.sharedctypes import Value

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

#region calculation of sfls

def __convert_dict_data(data):
    if isinstance(data, str):
        yield data
    elif isinstance(data, bool):
        yield '1' if data else '0'
    elif isinstance(data, int) or isinstance(data, float):
        yield str(data)
    elif data is None:
        pass
    elif isinstance(data, list):
        for element in data:
            for generator_element in __convert_dict_data(element):
                yield generator_element
    elif isinstance(data, dict):
        for key, value in sorted(data.items()):
            if not isinstance(key, str):
                raise TypeError("all the dictionay should be key string")
            
            yield key
            for generator_element in __convert_dict_data(value):
                yield generator_element
    else:
        raise ValueError('type not supported')

def __calculate_slfs(request: dict):
    if 'slfs' in request:
        raise ValueError('the request should no contains a slfs key')

    plain_slfs_tokens = []

    for token in __convert_dict_data(request):
        plain_slfs_tokens.append(token)

    md5_alg = hashlib.md5()
    
    for slfs_tokens in plain_slfs_tokens:
        md5_alg.update(slfs_tokens.encode('utf-8'))

    return md5_alg.hexdigest()

#endregion

def __request_have_valid_SLFS(request):
    if not 'slfs' in request or not 'lt' in request:
        return False

    request_without_slfs = request.copy()
    del request_without_slfs['slfs']

    correct_slfs = __calculate_slfs(request_without_slfs)

    return request['slfs'] == correct_slfs

def parse_request(specification, fields_converter = None):
    """take the flask's request obj and parse it with the business logic to return it.

    Args:
        specification (dict[str, any]): a dictionary that contains the specification of how parse the request and when it will be invalid (cerberus api)
        fields_converter (dict[str, any], optional): a dictionary that contains in the keys the path dotted notation of where in the request dict you wanna convert and in the value a function that accept the current value and transfomr it. Defaults to None.

    Returns:
        tuple[bool, dict]: returns a tuple
            [0] contains if the request is valid\n
            [1] contains the parsed request if is valid. otherwise will be None
    """
    
    if not request.is_json:
        return (False, None)

    specification['lt'] = {'type': 'string', 'required': True}
    specification['slfs'] = {'type': 'string', 'required': True}

    valid_request = normalize_and_validate(specification, request.json)

    if not valid_request:
        return (False, None)

    if not __request_have_valid_SLFS(valid_request):
        return (False, None)

    valid_request = own_json.process_json_obj(valid_request)

    if fields_converter:
        __convert_fields_of_dict(valid_request, fields_converter)

    return (True, valid_request)