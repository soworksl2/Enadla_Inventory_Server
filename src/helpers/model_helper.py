import inspect

def __remove_extra_fields(args_dict: dict, cls):
    
    parameters_allowed = inspect.signature(cls).parameters
    parameters = {}

    for key, value in args_dict.items():
        if key in parameters_allowed:
            parameters[key] = value
    
    return parameters
    
def create_obj(cls_to_create, ignore_extra_fields = True, **kwargs):
    """generate an obj calling its ctor

    Args:
        cls_to_create (callable): the class with the init to construct
        ignore_extra_fields (bool, optional): if the extra fields passed to ctor will be ignored. Defaults to True.

    Returns:
        instance: an instance of the specificated ctor
    """

    parameters_to_ctor = __remove_extra_fields(kwargs, cls_to_create) if ignore_extra_fields else kwargs

    return cls_to_create(**parameters_to_ctor)