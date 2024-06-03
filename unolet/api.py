import requests


class UnoletAPI:
    token = None
    base_url = None
    api_version = None
    api_url = None

    @classmethod
    def connect(cls, token, base_url, api_version="v1"):
        cls.token = token
        cls.base_url = base_url
        cls.api_version = api_version
        cls.api_url = f"{base_url}/api/{api_version}"

    @staticmethod
    def _get_headers():
        return {
            "Authorization": f"Token {UnoletAPI.token}",
            "Content-Type": "application/json",
        }

    @staticmethod
    def _request(endpoint, method='GET', params=None, data=None):
        url = UnoletAPI._build_url(endpoint)
        print(method, url)
        print(params)
        print(data)
        headers = UnoletAPI._get_headers()
        response = requests.request(method, url, headers=headers, params=params, json=data)
        return response

    @staticmethod
    def _get(endpoint, params=None):
        response = UnoletAPI._request(endpoint, "GET", params=params)
        return UnoletAPI._process_response(response)

    @staticmethod
    def _post(endpoint, params=None, data=None):
        response = UnoletAPI._request(endpoint, "POST", params=params, data=data)
        return UnoletAPI._process_response(response)

    @staticmethod
    def _put(endpoint, params=None, data=None):
        response = UnoletAPI._request(endpoint, "PUT", params=params, data=data)
        return UnoletAPI._process_response(response)

    @staticmethod
    def _patch(endpoint, params=None, data=None):
        response = UnoletAPI._request(endpoint, "PATCH", params=params, data=data)
        return UnoletAPI._process_response(response)

    @staticmethod
    def _delete(endpoint, params=None):
        response = UnoletAPI._request(endpoint, "DELETE", params=params)
        return UnoletAPI._process_response(response)

    @staticmethod
    def _options(endpoint):
        response = UnoletAPI._request(endpoint, "OPTIONS")
        return UnoletAPI._process_response(response)

    @staticmethod
    def _process_response(response: requests.Response):
        return response

    @staticmethod
    def _build_url(endpoint: str):
        assert not endpoint.startswith("/") and not endpoint.endswith("/")
        return f"{UnoletAPI.api_url}/{endpoint}/"

