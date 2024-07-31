import requests
from dataclasses import dataclass

from unolet.exceptions import handle_response_error


@dataclass(frozen=True)
class APIConfig:
    token: str
    base_url: str
    api_version: str = "v1"

    @property
    def api_url(self):
        return f"{self.base_url}/api/{self.api_version}"


class UnoletAPI:
    config: APIConfig = None

    @classmethod
    def connect(cls, token: str, base_url: str, api_version: str = "v1"):
        """
        Establish a connection to the Unolet API.

        This method configures the connection settings for the Unolet API using
        the provided token, base URL, and API version.

        Args:
            `token` (str): The authentication token for accessing the Unolet API.
            `base_url` (str): The base URL of the Unolet API.
            `api_version` (str, optional): The version of the Unolet API to use. Defaults to "v1".
        """
        cls.config = APIConfig(token, base_url, api_version)

    @staticmethod
    def get_headers():
        return {
            "Authorization": f"Token {UnoletAPI.config.token}",
            "Content-Type": "application/json",
        }

    @staticmethod
    def request(endpoint, method='GET', params=None, data=None):
        url = UnoletAPI.build_url(endpoint)
        headers = UnoletAPI.get_headers()
        response = requests.request(method, url, headers=headers, params=params, json=data)
        return response

    @staticmethod
    def get(endpoint, params=None):
        response = UnoletAPI.request(endpoint, "GET", params=params)
        return UnoletAPI.process_response(response)

    @staticmethod
    def post(endpoint, params=None, data=None):
        response = UnoletAPI.request(endpoint, "POST", params=params, data=data)
        return UnoletAPI.process_response(response)

    @staticmethod
    def put(endpoint, params=None, data=None):
        response = UnoletAPI.request(endpoint, "PUT", params=params, data=data)
        return UnoletAPI.process_response(response)

    @staticmethod
    def patch(endpoint, params=None, data=None):
        response = UnoletAPI.request(endpoint, "PATCH", params=params, data=data)
        return UnoletAPI.process_response(response)

    @staticmethod
    def delete(endpoint, params=None):
        response = UnoletAPI.request(endpoint, "DELETE", params=params)
        return UnoletAPI.process_response(response)

    @staticmethod
    def options(endpoint):
        response = UnoletAPI.request(endpoint, "OPTIONS")
        return UnoletAPI.process_response(response)

    @staticmethod
    def process_response(response: requests.Response):
        handle_response_error(response)
        return response

    @staticmethod
    def build_url(endpoint: str):
        assert not endpoint.startswith("/") and not endpoint.endswith("/")
        return f"{UnoletAPI.config.api_url}/{endpoint}/"

