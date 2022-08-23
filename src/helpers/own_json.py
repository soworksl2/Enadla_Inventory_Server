"""module that contains methods for serialize or deserialize objs following the enadla_inventory rules
"""

import json
from datetime import datetime

def __is_json_suportable_type(obj):
    return \
        isinstance(obj, str) or\
        isinstance(obj, int) or\
        isinstance(obj, float) or\
        isinstance(obj, bool) or\
        obj is None

def __datetime_serialization(datetime_to_serialize: datetime):
    if not isinstance(datetime_to_serialize, datetime):
        raise TypeError('the obj is not a datetime')

    if datetime_to_serialize.tzinfo is None:
        raise ValueError('the datetime need a tzinfo')

    return datetime_to_serialize.strftime('%Y-%m-%d %H:%M:%S %z')

def __default_serialization(obj_to_serialize):
    if isinstance(obj_to_serialize, datetime):
        return __datetime_serialization(obj_to_serialize)
    else:
        try:
            return obj_to_serialize.__dict__
        except:
            raise TypeError(f'{type(obj_to_serialize)} cannot be serialized')

def dumps(obj):
    """serialize an obj or a dict to string

    Args:
        obj (obj_dict_convertible | dict): the object that can be able to convert to dict or the dict to serialize

    Returns:
        str: the str obj serialized
    """

    if not isinstance(obj, dict) and not isinstance(obj, list):
        obj = obj.__dict__

    return json.dumps(obj, default=__default_serialization)

def __process_datetime_format(datetime_str: str):
    DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S %z'
    try:
        output = datetime.strptime(datetime_str, DATETIME_FORMAT)
    except:
        output = None
    return output

def __process_str(str_to_process: str):
    output = __process_datetime_format(str_to_process)
    if output:
        return output

    return str_to_process

def __process_value(value):
    if isinstance(value, str):
        return __process_str(value)
    
    if isinstance(value, list):
        return __process_list(value)

    if isinstance(value, dict):
        return __process_dict(value)
    
    return value

def __process_dict(dict_to_process: dict):
    new_dict = {}

    for key, value in dict_to_process.items():
        new_dict[key] = __process_value(value)
    
    return new_dict

def __process_list(list_to_process: list):
    new_list = []

    for value in list_to_process:
        new_list.append(__process_value(value))
    
    return new_list

def process_json_obj(json_obj: dict | list):
    if not isinstance(json_obj, dict) and not isinstance(json_obj, list):
        raise TypeError('the json obj should be a list or a dict')

    return __process_dict(json_obj) if isinstance(json_obj, dict) else __process_list(json_obj)