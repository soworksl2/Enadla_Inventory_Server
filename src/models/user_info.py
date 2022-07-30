from datetime import datetime
from dataclasses import dataclass
from enum import Enum

import pytz

from helpers import validation_functions as v
from helpers import model_helper

@dataclass
class ExtraUserInfo:

    uid: str = None
    creation_date: datetime = None
    creator_machine: str = None

    def __post_init__(self):
        if self.creation_date is None:
            self.creation_date = datetime.now(tz=pytz.UTC)

    @classmethod
    def from_dict(cls, **kwargs):
        return model_helper.create_obj(cls, **kwargs)


@dataclass
class UserInfo:
    
    uid: str = None
    email: str = None
    password: str = None
    is_verified: bool = False
    owner_name: str = None
    extra_info: ExtraUserInfo = None

    @classmethod
    def from_dict(cls, **kwargs):
        """create a UserInfo from a dictionary ignoring the extra fields

        Returns:
            UserInfo: the created UserInfo
        """

        instance = model_helper.create_obj(cls, **kwargs)

        if instance.extra_info is not None and not isinstance(instance.extra_info, ExtraUserInfo):
            instance.extra_info = ExtraUserInfo.from_dict(instance.extra_info)
        
        return instance


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

def __sign_up_validation(user_info: UserInfo):
    
    fails = []


    if v.is_empty_str(user_info.email):
        fails.append(ValidationFails.empty_email)

    if not v.is_valid_email(user_info.email):
        fails.append(ValidationFails.invalid_email)

    if v.is_empty_str(user_info.password):
        fails.append(ValidationFails.empty_password)

    if v.is_empty_str(user_info.owner_name):
        fails.append(ValidationFails.empty_owner_name)

    if not v.len_min(3, user_info.owner_name):
        fails.append(ValidationFails.short_owner_name)

    if not v.len_max(50, user_info.owner_name):
        fails.append(ValidationFails.long_owner_name)

    #extra info validations

    if not __has_extra_info(user_info) or v.is_empty_str(user_info.extra_info.creator_machine):
        fails.append(ValidationFails.empty_creator_machine)

    fails = set(fails)
    return (len(fails) <= 0, fails)

def validate(user_info, rule_set):
    if rule_set == R_SIGNUP:
        return __sign_up_validation(user_info)
    else:
        raise ValueError(f'"{rule_set}" is an invalid rule')