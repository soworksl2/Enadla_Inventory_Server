import datetime

def default_dump(obj_to_dump):
    if isinstance(obj_to_dump, datetime.datetime):
        return obj_to_dump.strftime('%Y-%m-%dT%H:%M:%S')
    else:
        raise TypeError(f'{type(obj_to_dump).__name__} is no serializable')
