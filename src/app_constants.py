"""constants for the application
"""

import os

def get_web_api_key():
    """returns the web api key of this project

    Returns:
        str: the firebase web api key
    """

    output = os.environ['WEB_API_KEY']
    return output

def get_init_tokens_on_signUp():
    """returns the amoun of tokens that an user will get when he signUp in endadla

    Raises:
        ValueError: if the INIT_TOKENS_ON_SIGNUP is minor than 0

    Returns:
        int: the amount of tokens that an user will get on signup
    """
    
    output = int(os.environ['INIT_TOKENS_ON_SIGNUP'])

    if output < 0:
        raise ValueError('the INIT_TOKENS_ON_SIGNUP cannot be minor than 0')

    return output

def get_range_for_max_signUp():
    """returns the range of days for the max signup per machine that a machine can do

    Raises:
        ValueError: if the value is minor than 1

    Returns:
        int: the range for max signUp per machine that the machine can do
    """

    output = os.environ['RANGE_FOR_MAX_SIGNUP']
    output = int(output)

    if output < 1:
        raise ValueError('the RANGE_FOR_MAX_SIGNUP cannot be minor than 1')

    return output

def get_max_signUp_per_machine_in_range():
    """returns the max signup per machine that a machine can do in a determined range of days

    Raises:
        ValueError: if the value is minor tha 1

    Returns:
        int: the max signup per machine that a machine can do
    """

    output = os.environ['MAX_SIGNUP_PER_MACHINE_IN_RANGE']
    output = int(output)

    if output < 1:
        raise ValueError("The MAX_SIGNUP_PER_MACHINE_IN_RANGE cannot be minor than 1")
    
    return output

def get_last_compatible_client_version():
    version_str = os.environ['LAST_COMPATIBLE_CLIENT_VERSION']
    try:
        major, minor, patch = [int(version) for version in version_str.split('.')]
    except:
        raise ValueError('LAST_COMPATIBLE_CLIENT_VERSION')

    if any(version < 0 for version in [major, minor, patch]):
        raise ValueError('LAST_COMPATIBLE_CLIENT_VERSION')

    return (major, minor, patch)

def get_machine_link_locked_time():
    """return the time in days that a machina can be locked upto it can be updated

    Returns:
        int: the time in dayss that a machine can be locked
    """

    output = os.environ['MACHINE_LINK_LOCKED_TIME']
    output = int(output)

    return output