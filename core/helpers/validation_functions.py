"""multiple functions to make validation more easy
"""

import re

def is_empty_str(string):
    """check if an str is empty (0 lengh, white spaces or None)

    Args:
        string (str): the string to check

    Returns:
        bool: wheter the string is empty or not
    """
        
    if string is None:
        return True

    string = string.strip()

    if string == "":
        return True
    return False

def is_valid_email(email):
    """check if a str is a valid email

    Args:
        email (str): the str that represent the email

    Returns:
        bool: wheter the email is valid or not
    """
    
    if email is None or not isinstance(email, str):
        return False

    EMAIL_REGEX = "([-!#-'*+/-9=?A-Z^-~]+(\.[-!#-'*+/-9=?A-Z^-~]+)*|\"([]!#-[^-~ \t]|(\\[\t -~]))+\")@([-!#-'*+/-9=?A-Z^-~]+(\.[-!#-'*+/-9=?A-Z^-~]+)*|\[[\t -Z^-~]*])"

    if re.search(EMAIL_REGEX,email):   
        return True  
    
    return False

def len_min(min_len, enumerable):
    """checks if the lenght of an object is the minimun specificated or greather

    Args:
        min_len (int): the minimun lenght that the object should have
        enumerable (any): an obj that have the __len__ function or iterable to check the lenght

    Raises:
        ValueError: if the min_len is minor than 0

    Returns:
        bool: True if the obj has a lenght greather or equals to the min_len specificated else False
    """

    if min_len < 0:
        raise ValueError('min_len cannot be minor than 0')

    lenght = len(enumerable) if enumerable is not None else 0

    return lenght >= min_len

def len_max(max_len, enumerable):
    """checks if an obj is minor than the specificated max_lenght

    Args:
        max_len (int): the maximun leght that the obj should have
        enumerable (iterable): the obj to checks its lenght

    Raises:
        ValueError: if the max_len is minor or equals to 0

    Returns:
        bool: True if the obj has a lenght minor or equals to the specificated max_len
    """

    if max_len <= 0:
        raise ValueError('max_len cannot be minor or equals to 0')

    lenght = len(enumerable) if enumerable is not None else 0

    return lenght <= max_len