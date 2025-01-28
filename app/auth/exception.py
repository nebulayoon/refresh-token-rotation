from fastapi import status

from app.exception import CustomException


class NotFoundUser(CustomException):
    status_code: int = status.HTTP_400_BAD_REQUEST
    message: str = "User not found"


class IncorrectEmailOrPassword(CustomException):
    status_code: int = status.HTTP_400_BAD_REQUEST
    message: str = "Incorrect Email or Password"


class TokenException(CustomException):
    status_code: int = status.HTTP_400_BAD_REQUEST
    message: str = "Token Error"


class TokenInvalidException(TokenException):
    status_code: int = status.HTTP_401_UNAUTHORIZED
    message: str = "Token Invailid"


class DuplicateEmailException(CustomException):
    status_code: int = status.HTTP_400_BAD_REQUEST
    message = "Duplicate email"


class UserNotFoundException(CustomException):
    status_code: int = status.HTTP_404_NOT_FOUND
    message = "User not found"


class NoEmailOrWrongPassword(CustomException):
    status_code: int = status.HTTP_404_NOT_FOUND
    message = "Invalid Email or Password"


class InvalidCharacterException(CustomException):
    status_code: int = status.HTTP_400_BAD_REQUEST
    message = "Invalid password"
