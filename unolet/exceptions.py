import requests


class UnoletError(Exception):
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


def handle_response_error(response: requests.Response):
    try:
        response.raise_for_status()
    except Exception as e:
        try:
            errors = response.json()
        except Exception:
            errors = None
        raise UnoletError(errors=errors, response=response)