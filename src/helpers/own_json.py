"""module that contains methods for serialize or deserialize objs following the enadla_inventory rules
"""

import json
from datetime import datetime

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
        raise TypeError(f'{type(obj_to_serialize)} cannot be serialized')

def serialize_to_str(obj):
    """serialize an obj or a dict to string

    Args:
        obj (obj_dict_convertible | dict): the object that can be able to convert to dict or the dict to serialize

    Returns:
        str: the str obj serialized
    """

    if not isinstance(obj, dict):
        obj = obj.__dict__

    return json.dumps(obj, default=__default_serialization)