INVALID_USERINFO = 'INVALID_USERINFO'
EMAIL_CONFLICT = 'EMAIL_CONFLICT'
INVALID_CREDENTIALS = 'INVALID_CREDENTIALS'
USER_NOT_EXISTS_OR_DISABLE = 'USER_NOT_EXISTS_OR_DISABLE'
UNVERIFIED_USER = 'UNVERIFIED_USER'
TOO_MANY_SIGN_UP = 'TOO_MANY_SIGN_UP'
HTTP_BASIC_ERROR = 'HTTP_BASIC_ERROR'
UNEXPECTED_ERROR = 'UNEXPECTED_ERROR'

#app_error_code in execption form

class InvalidUserinfoException(Exception):
    pass

class EmailConflictException(Exception):
    pass

class InvalidCredentialsException(Exception):
    pass

class UserNotExistsOrDisableException(Exception):
    pass

class UnverifiedUserException(Exception):
    pass

class TooManySignUpException(Exception):
    pass

class HTTPBasicErrorException(Exception):
    pass

class UnexpectedError(Exception):
    pass