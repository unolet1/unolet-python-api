from datetime import datetime
from decimal import Decimal
from types import SimpleNamespace

import requests

from unolet.api import UnoletAPI
from unolet.utils import (
    is_string_decimal,
    string_to_date,
    date_to_string,
)
from unolet.exceptions import (
    UnoletError,
    ObjectDoesNotExist,
    handle_response_error,
)


class UnoletResource(SimpleNamespace, UnoletAPI):
    endpoint = None

    def __init__(self, **kwargs):
        items = list(kwargs.items())
        self._changes = {}
        self._errors = {}

        for k,v in items:
            kwargs[k] = self.__parse_value(v)

        super().__init__(**kwargs)

    def __setattr__(self, key, value):
        if key in self.__dict__ and self.__dict__[key] != value:
            self._changes[key] = value
        super().__setattr__(key, value)

    def __parse_value(self, value):
        if isinstance(value, dict):
            if 'id' in value:
                value = UnoletResource(**value)
        if isinstance(value, list):
            value = [self.__parse_value(e) for e in value]
        if isinstance(value, str):
            try:
                value = string_to_date(value)
            except ValueError:
                if is_string_decimal(value):
                    value = Decimal(value)
        return value

    @classmethod
    def find(cls, **params):
        endpoint = cls.endpoint
        data = cls._get(endpoint, params)
        return [cls(**item) for item in data]

    @classmethod
    def get(cls, id):
        endpoint = f"{cls.endpoint}/{id}"
        response = cls._get(endpoint)

        if response.status_code == 404:
            raise ObjectDoesNotExist(response)

        data = response.json()
        return cls(**data)

    @classmethod
    def create(cls, data):
        endpoint = cls.endpoint
        response = cls._post(endpoint, data=data)
        return response

    def delete(self):
        endpoint = f"{self.endpoint}/{self.id}"
        response = self._delete(endpoint)
        self._validate(response)
        return response.status_code == 204

    def update(self):
        assert self.id
        if self._changes:
            endpoint = f"{self.endpoint}/{self.id}"
            data = self._changes
            response = self._patch(endpoint, data=data)
            updated_data = self._validate(response)
            self._update_from_data(updated_data)

    def _update_from_data(self, data):
        self.__init__(**data)

    def _refresh_from_api(self):
        assert self.id
        instance = self.get(self.id)
        self._update_from_data(instance.as_dict())

    def save(self, *args, **kwargs):
        if self.id:
            self.update()
        else:
            response = self.create(self.as_dict())
            data = self._validate(response)
            self._update_from_data(data)

    def _validate(self, response):
        handle_response_error(response)
        try:
            return response.json()
        except requests.exceptions.JSONDecodeError:
            pass

    def exists(self):
        assert self.id
        try:
            self.get(self.id)
        except ObjectDoesNotExist:
            return False
        return True

    def as_dict(self):
        return self._serialize(self)

    @staticmethod
    def _serialize(obj):
        if isinstance(obj, UnoletResource):
            dic = vars(obj)
            return UnoletResource._serialize(dic)
        if isinstance(obj, list):
            return [UnoletResource._serialize(item) for item in obj]
        if isinstance(obj, dict):
            return {k: UnoletResource._serialize(v) for k, v in obj.items()}
        if isinstance(obj, datetime):
            return date_to_string(obj)
        if isinstance(obj, Decimal):
            return str(obj)
        return obj