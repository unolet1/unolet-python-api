from datetime import date, datetime
from decimal import Decimal
from functools import cached_property
from types import SimpleNamespace
from collections import defaultdict
from typing import Dict, List, Optional
from urllib.parse import urlparse, parse_qs

from unolet.api import UnoletAPI
from unolet.utils import is_string_decimal, string_to_date
from unolet.exceptions import ObjectDoesNotExist, ValidationError
from unolet.fields import RELATED, Field, Undefined, field_mapping


class ResourceMeta(type):
    def __new__(cls, name, bases, dct):
        if "_endpoint" not in dct:
            raise AttributeError(f"Class {name} must define '_endpoint' attribute")
        dct['_metadata'] = None
        return super().__new__(cls, name, bases, dct)

    def __init__(cls, name, bases, dct):
        super().__init__(name, bases, dct)


class State:
    def __init__(self, original_data):
        self.changes = {}
        self.adding = False
        self.original_data = original_data or {}


class Metadata:
    def __init__(self, data):
        """
        Initialize metadata with the provided data.

        Args:
            data (dict): Data to initialize metadata.
        """
        self.name = data.get("name", "")
        self.description = data.get("description", "")
        self.actions = data.get("actions", {})
        _fields_dict = self.actions.get("POST", self.actions.get("PUT", {}))
        self.fields: Dict[str, Field] = {}
        for field_name, field_data in _fields_dict.items():
            if "child" in field_data:
                field_class = field_mapping[RELATED]
            else:
                field_class = field_mapping[field_data["type"]]

            field = field_class(field_name, **field_data)
            self.fields[field_name] = field

    def __str__(self):
        return f"Metadata: {self.name}"

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.name}>"


class BaseResource(SimpleNamespace, metaclass=ResourceMeta):
    _endpoint = None

    def __init__(self, **kwargs):
        self._initialize_metadata()
        self._state = State(kwargs)

        initial_data = self._get_initial_data(kwargs)
        if initial_data.get("id") is Undefined:
            initial_data["id"] = None
            self._state.adding = True
        super().__init__(**initial_data)

    def __setattr__(self, key, value):
        if key in self.__dict__ and self.__dict__[key] != value:
            self._state.changes[key] = value
        super().__setattr__(key, value)

    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, self)

    def __str__(self):
        return "%s object (%s)" % (self.__class__.__name__, self.id)

    def __eq__(self, other):
        if not isinstance(other, BaseResource):
            return NotImplemented
        return self.id == other.id if self.id is not None else self is other

    def __hash__(self):
        if self.id is None:
            raise TypeError("Resource instances without id value are unhashable.")
        return hash(self.id)

    @classmethod
    def _initialize_metadata(cls):
        if cls._metadata is None:
            response = UnoletAPI.options(cls._endpoint)
            if response.status_code == 200:
                cls._metadata = Metadata(response.json())
            else:
                cls._metadata = Metadata({})

    def _get_initial_data(self, data):
        initial_data = {}
        for field_name, field in self._metadata.fields.items():
            value = data.get(field_name, Undefined)
            initial_data[field_name] = field.parse_value(value)
        return initial_data

    def _update_from_data(self, data):
        self.__init__(**data)

    def _refresh_from_api(self):
        assert self.id
        instance = self.get(self.id)
        self._update_from_data(instance.as_dict())

    def _validate_data(self, data):
        validated_data = {}
        errors = defaultdict(list)

        for field_name, field in self._metadata.fields.items():
            value = data.get(field_name, Undefined)

            if field.read_only:
                continue

            if field.required and value is Undefined:
                errors[field_name].append(f"This field is required.")
                continue

            if value is not Undefined:
                try:
                    validated_value = field.serialize(value)
                    validated_data[field_name] = validated_value
                except ValueError as e:
                    errors[field_name].append(f"Invalid type for this field: {e}")

        if errors:
            raise ValidationError(dict(errors))

        return validated_data

    def save(self):
        data = {k: v for k, v in self.__dict__.items() if not k.startswith('_')}
        validated_data = self._validate_data(data)
        if self._state.adding:
            response = self.create(validated_data)
        else:
            response = self.update(validated_data)
        data = response.json()
        self._update_from_data(data)
        return self

    @classmethod
    def find(cls, **params):
        response = UnoletAPI.get(cls._endpoint, params)
        data = response.json()
        if "count" in data:
            return Pagination(
                model_class=cls,
                count=data["count"],
                next_url=data["next"],
                previous_url=data["previous"],
                results=data["results"]
            )
        elif "results" in data:
            return ResourceList(model_class=cls, items=data)
        raise NotImplemented()

    @classmethod
    def get(cls, id):
        response = UnoletAPI.get(f"{cls._endpoint}/{id}")

        if response.status_code == 404:
            raise ObjectDoesNotExist(response)

        data = response.json()
        return cls(**data)

    @classmethod
    def create(cls, data):
        response = UnoletAPI.post(cls._endpoint, data=data)
        return response

    def delete(self):
        response = UnoletAPI.delete(f"{self._endpoint}/{self.id}")
        return response.status_code == 204

    def update(self):
        assert self.id
        if self._state.changes:
            data = self._state.changes
            data = {k: self._serialize(v) for k, v in data.items()}
            response = UnoletAPI.patch(f"{self._endpoint}/{self.id}", data=data)
            updated_data = response.json()
            self._update_from_data(updated_data)

    def exists(self):
        assert self.id
        if not self.id:
            return False
        try:
            self.get(self.id)
        except ObjectDoesNotExist:
            return False
        return True

    def _serialize(self):
        serialized_data = {}
        for field_name, field in self._metadata.fields.items():
            value = getattr(self, field_name, None)
            if value is not None:
                if field.internal_type == Decimal:
                    serialized_data[field_name] = str(value)
                elif field.internal_type in [datetime, date]:
                    serialized_data[field_name] = value.isoformat()
                else:
                    serialized_data[field_name] = value
        return serialized_data

    def _deserialize(self, data):
        deserialized_data = {}
        for field_name, field in self._metadata.fields.items():
            value = data.get(field_name, None)
            if value is not None:
                if field.internal_type == Decimal:
                    deserialized_data[field_name] = Decimal(value)
                elif field.internal_type == datetime:
                    deserialized_data[field_name] = datetime.fromisoformat(value)
                elif field.internal_type == date:
                    deserialized_data[field_name] = date.fromisoformat(value)
                elif field.internal_type == int:
                    deserialized_data[field_name] = int(value)
                elif field.internal_type == float:
                    deserialized_data[field_name] = float(value)
                elif field.internal_type == str:
                    deserialized_data[field_name] = str(value)
                elif field.internal_type == bool:
                    deserialized_data[field_name] = value.lower() in ['true', '1', 't', 'y', 'yes']
        self._update_from_data(deserialized_data)


class UnoletResource(BaseResource):
    _endpoint = None


class ResourceList:
    def __init__(self, model_class: UnoletResource, items: List[Dict]):
        """
        Initialize a ResourceList.

        Args:
            model_class (UnoletResource): The class of the resource.
            items (List[Dict]): The items to include in the resource list.
        """
        self.model_class = model_class
        self.items = [model_class(**item) for item in items]

    def __repr__(self) -> str:
        return f"<ResourceList(items={self.items})>"

    def __str__(self) -> str:
        return f"ResourceList({self.model_class.__name__})"

    def __len__(self) -> int:
        return len(self.items)

    def __getitem__(self, index: int) -> UnoletResource:
        return self.items[index]

    def __iter__(self):
        return iter(self.items)

    def __eq__(self, other: 'ResourceList') -> bool:
        if not isinstance(other, ResourceList):
            return NotImplemented
        return self.items == other.items

    @cached_property
    def count(self):
        return len(self)


class Pagination:
    def __init__(self, model_class: UnoletResource, count: int, next_url: Optional[str], previous_url: Optional[str], results: List[Dict]):
        """
        Initialize a Pagination object.

        Args:
            model_class (UnoletResource): The class of the resource.
            count (int): The total number of results.
            next_url (Optional[str]): The URL for the next page of results.
            previous_url (Optional[str]): The URL for the previous page of results.
            results (List[Dict]): The list of results.
        """
        self.model_class = model_class
        self.count = count
        self.next_url = next_url
        self.previous_url = previous_url
        self.results = ResourceList(model_class, results)

        if self.next_url:
            self.next_url_params = parse_qs(urlparse(self.next_url).query)
        if self.previous_url:
            self.previous_url_params = parse_qs(urlparse(self.previous_url).query)

    def __repr__(self) -> str:
        return f"<Pagination(count={self.count}, next={self.next_url}, previous={self.previous_url}, results={self.results})>"

    def __str__(self) -> str:
        return f"Pagination with {self.count} results, next: {self.next_url}, previous: {self.previous_url}"

    def __len__(self) -> int:
        return self.count

    def __getitem__(self, index: int) -> UnoletResource:
        return self.results[index]

    def __iter__(self):
        return iter(self.results)

    def __eq__(self, other: 'Pagination') -> bool:
        if not isinstance(other, Pagination):
            return NotImplemented
        return self.count == other.count and self.next_url == other.next and self.previous_url == other.previous and self.results == other.results

    def next(self):
        if self.next_url:
            page = self.next_url_params["page"][0]
            return self.model_class.find(page=page)

    def previous(self):
        if self.previous_url:
            page = self.previous_url_params["page"][0]
            return self.model_class.find(page=page)
