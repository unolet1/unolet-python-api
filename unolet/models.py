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
from unolet.fields import Undefined, field_mapping

class State:
    def __init__(self, original_data):
        self.changes = {}
        self.adding = False
        self.original_data = original_data or {}


class Metadata:
    def __init__(self, data):
        self.name = data.get("name", "")
        self.description = data.get("description", "")
        self.actions = data.get("actions", {})
        _fields_dict = self.actions.get("POST", self.actions.get("PUT", {}))
        self.fields = {}
        for field_name, field_data in _fields_dict.items():
            if "child" in field_data:
                field_class = field_mapping["related"]
            else:
                field_class = field_mapping[field_data["type"]]

            field = field_class(field_name, field_data)
            self.fields[field_name] = field

    def __str__(self):
        return f"Metadata: {self.name}"

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.name}>"


class UnoletResource(SimpleNamespace, UnoletAPI):
    _endpoint = None
    _metadata = None

    def __init__(self, **kwargs):
        self.__class__._initialize_metadata()
        self._state = State(kwargs)

        initial_data = {}
        for field_name, field in self._metadata.fields.items():
            value = kwargs.get(field_name, Undefined)
            initial_data[field_name] = self._parse_value(value)

        if not "id" in initial_data or initial_data["id"] is Undefined:
            initial_data["id"] = None
            self._state.adding = True

        super().__init__(**initial_data)

    def __setattr__(self, key, value):
        if key in self.__dict__ and self.__dict__[key] != value:
            self._state.changes[key] = value
        super().__setattr__(key, value)

    @classmethod
    def _initialize_metadata(cls):
        if cls._metadata is None:
            response = cls._options(cls._endpoint)
            if response.status_code == 200:
                cls._metadata = Metadata(response.json())
            else:
                cls._metadata = Metadata()

    def _parse_value(self, value):
        if isinstance(value, dict):
            if 'id' in value:
                value = UnoletResource(**value)
        if isinstance(value, list):
            value = [self._parse_value(e) for e in value]
        if isinstance(value, str):
            try:
                value = string_to_date(value)
            except ValueError:
                if is_string_decimal(value):
                    value = Decimal(value)
        return value

    @classmethod
    def find(cls, **params):
        data = cls._get(cls._endpoint, params)
        return [cls(**item) for item in data]

    @classmethod
    def get(cls, id):
        response = cls._get(f"{cls._endpoint}/{id}")

        if response.status_code == 404:
            raise ObjectDoesNotExist(response)

        data = response.json()
        return cls(**data)

    @classmethod
    def create(cls, data):
        response = cls._post(cls._endpoint, data=data)
        return response

    def delete(self):
        response = self._delete(f"{self._endpoint}/{self.id}")
        self._validate(response)
        return response.status_code == 204

    def update(self):
        assert self.id
        if self._state.changes:
            data = self._state.changes
            data = {k:self._serialize(v) for k,v in data.items()}
            response = self._patch(f"{self._endpoint}/{self.id}", data=data)
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
            response = self.create(self.get_form_data())
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

    def get_form_data(self):
        return self.as_dict(as_form_data=True)

    def as_dict(self, as_form_data=False):
        fields = self._metadata.fields
        data = {}
        for field_name, field in fields.items():
            value = getattr(self, field_name)

            if as_form_data:
                if field.read_only:
                    continue
                elif field.type == "object":
                    if isinstance(value, UnoletResource):
                        value = value.id
                if not value and field.required:
                    raise ValueError(f"Field {field_name} is required.")

            value = self._serialize(value)
            data[field_name] = value
        return data

    @staticmethod
    def _serialize(obj):
        if isinstance(obj, UnoletResource):
            dic = vars(obj)
            return UnoletResource._serialize(dic)
        elif isinstance(obj, list):
            return [UnoletResource._serialize(item) for item in obj]
        elif isinstance(obj, dict):
            return {k: UnoletResource._serialize(v) for k, v in obj.items()}
        elif isinstance(obj, datetime):
            return date_to_string(obj)
        elif isinstance(obj, Decimal):
            return str(obj)
        elif obj is Undefined:
            return None
        return obj