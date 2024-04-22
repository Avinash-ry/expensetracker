from rest_framework.exceptions import APIException
from rest_framework import status


class PasswordDidnotMatch(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Password didn't match"
    default_code = "password_didnot_match"


class InvalidCredentials(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Invalid Credentials"
    default_code = "invalid_credentials"


class InactiveAccount(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Your account has been deactivated! Please contact support."
    default_code = "inactive_account"


class UserNotFound(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "User not found."
    default_code = "user_not_found"


class HostNameNotFound(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Host-Name not found"
    default_code = "hostname_not_found"


class InvalidCurrentPassword(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "Invalid current password"
    default_code = "invalid_current_password"
