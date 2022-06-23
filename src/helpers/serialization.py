import datetime

def defaultDump(objToDump):
    if isinstance(objToDump, datetime.datetime):
        return objToDump.strftime('%Y-%m-%dT%H:%M:%S')
    else:
        raise TypeError(f'{type(objToDump).__name__} is no serializable')
