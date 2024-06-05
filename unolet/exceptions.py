import requests


NON_FIELD_ERRORS = "non_field_errors"


class UnoletError(Exception):
    pass


class APIError(UnoletError):
    """Base exception for errors related to connection with Unolet ERP."""

    __message = "An error has occurred"

    def __init__(self, message=None, errors=None, response: requests.Response=None):
        self.response = response
        self.errors = errors
        self.status_code = None
        if not message:
            message = errors.get('detail', errors) if errors else self.__message
        super().__init__(message)

    @property
    def messages(self):
        return [e2 for e2 in [e1 for e1 in self.errors.values()]]


class ObjectDoesNotExist(UnoletError):
    __message = "The object does not exist"


class ValidationError(UnoletError):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class RequiredFieldMissingError(ValidationError):
    pass


class ReadOnlyFieldError(ValidationError):
    pass


class InvalidFieldTypeError(ValidationError):
    pass


def handle_response_error(response: requests.Response):
    try:
        response.raise_for_status()
    except Exception as e:
        try:
            errors = response.json()
        except Exception:
            errors = None
        raise APIError(errors=errors, response=response)