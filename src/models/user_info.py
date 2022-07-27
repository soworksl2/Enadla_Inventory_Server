import re
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

import pytz

@dataclass
class ExtraUserInfo:

    uid: str = None
    creation_date: datetime = None
    creator_machine: str = None

    def __post_init__(self):
        if self.creation_date is None:
            self.creation_date = datetime.now(tz=pytz.UTC)


@dataclass
class UserInfo:
    
    uid: str = None
    email: str = None
    password: str = None
    is_verified: bool = False
    owner_name: str = None
    extra_info: ExtraUserInfo = None


# validation functions


R_SIGNUP = 'signup'

class ValidationFails(Enum):
    empty_email = 0
    invalid_email = 1
    empty_password = 2
    empty_owner_name = 3
    short_owner_name = 4
    long_owner_name = 5
    empty_creator_machine = 6

def __has_extra_info(user_info):
    return isinstance(user_info.extra_info, ExtraUserInfo)


def __is_empty_string(string: str):
    if string is None:
        return True

    string = string.strip()

    if string == "":
        return True
    return False

def __is_valid_email(email):
    if email is None or not isinstance(email, str):
        return False

    EMAIL_REGEX = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'

    if re.search(EMAIL_REGEX,email):   
        return True  
    
    return False

def __len_min(min_len, enumerable):
    
    if min_len < 0:
        raise ValueError('min_len cannot be minor than 0')

    lenght = len(enumerable) if enumerable is not None else 0

    return lenght >= min_len

def __len_max(max_len, enumerable):

    if max_len <= 0:
        raise ValueError('max_len cannot be minor or equals to 0')

    lenght = len(enumerable) if enumerable is not None else 0

    return lenght <= max_len

def __sign_up_validation(user_info: UserInfo):
    
    fails = []


    if __is_empty_string(user_info.email):
        fails.append(ValidationFails.empty_email)

    if not __is_valid_email(user_info.email):
        fails.append(ValidationFails.invalid_email)

    if __is_empty_string(user_info.password):
        fails.append(ValidationFails.empty_password)

    if __is_empty_string(user_info.owner_name):
        fails.append(ValidationFails.empty_owner_name)

    if not __len_min(3, user_info.owner_name):
        fails.append(ValidationFails.short_owner_name)

    if not __len_max(50, user_info.owner_name):
        fails.append(ValidationFails.long_owner_name)

    #extra info validations

    if not __has_extra_info(user_info) or __is_empty_string(user_info.extra_info.creator_machine):
        fails.append(ValidationFails.empty_creator_machine)

    fails = set(fails)
    return (len(fails) <= 0, fails)

def validate(user_info, rule_set):
    if rule_set == R_SIGNUP:
        return __sign_up_validation(user_info)
    else:
        raise ValueError(f'"{rule_set}" is an invalid rule')