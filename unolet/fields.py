from datetime import date, datetime
from decimal import Decimal
from functools import cached_property
from typing import Dict
import importlib

from unolet.utils import is_string_decimal, string_to_date, date_to_string


FIELD = "field"
RELATED = "nested object"
IMAGE = "image upload"
URL = "url"
EMAIL = "email"
STRING = "string"
INTEGER = "integer"
FLOAT = "float"
DECIMAL = "decimal"
CHOICE = "choice"
DATE = "date"
DATETIME = "datetime"
BOOLEAN = "boolean"


class Field:
    """
    Base class for all field types.
    """
    internal_type = None

    def __init__(self, name: str, **data):
        """
        Initialize a field with the given name and properties.

        Args:
            name (str): The name of the field.
            **data: Additional properties for the field.
        """
        self.name = name
        self.type = data.pop("type")
        self.required = data.pop("required")
        self.read_only = data.pop("read_only")
        self.allow_null = data.pop("allow_null")
        self.help_text = data.pop("help_text", "")
        self.label = data.pop("label", name.replace("_", " ").capitalize())

        # Other properties
        for key, value in data.items():
            setattr(self, key, value)

        self.validate_data()

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.name}>"

    @cached_property
    def is_related(self):
        """
        Check if the field is a related field.
        """
        return bool(getattr(self, "related_model", None))

    def validate_data(self):
        """
        Validate the field's data.
        """
        assert isinstance(self.name, str)
        assert isinstance(self.type, str)
        assert isinstance(self.required, bool)
        assert isinstance(self.read_only, bool)

    def validate_value(self, value):
        """
        Validate the value against the field's expected type.

        Args:
            value: The value to be validated.

        Returns:
            The validated value.
        """
        expected_type = self.internal_type
        if (
            value is not None
            and value is not Undefined
            and expected_type
            and not isinstance(value, expected_type)
        ):
            try:
                if expected_type == Decimal:
                    value = Decimal(str(value))
                elif expected_type in (datetime, date):
                    value = string_to_date(str(value))
                else:
                    value = expected_type(value)
            except (ValueError, TypeError):
                raise ValueError(f"expected an {expected_type.__name__}, but received {type(value).__name__} = {value}")
        return value

    def parse_value(self, value):
        """
        Parse the value to the appropriate type.

        Args:
            value: The value to be parsed.

        Returns:
            The parsed value.
        """
        value = self.validate_value(value)
        if self.is_related and isinstance(value, dict) and 'id' in value:
            module = importlib.import_module("unolet")
            model_class = getattr(module, self.related_model)
            value = model_class(**value)
        elif isinstance(value, list):
            value = [self.parse_value(e) for e in value]
        elif isinstance(value, str):
            try:
                value = string_to_date(value)
            except ValueError:
                if is_string_decimal(value):
                    value = Decimal(value)
        return value

    def serialize(self, value):
        """
        Serialize the value to a format suitable for a POST request with requests.

        Args:
            value (any): The value to be serialized.

        Returns:
            any: The serialized value.
        """
        if value is None:
            return value
        elif self.is_related:
            return value.id
        elif isinstance(value, (date, datetime)):
            return date_to_string(value)
        elif isinstance(value, Decimal):
            return str(value)
        elif isinstance(value, list):
            return [self.serialize(v) for v in value]
        elif hasattr(value, '__dict__'):
            return {k: self.serialize(v) for k, v in value.__dict__.items() if not k.startswith('_')}
        else:
            return value


class RelatedField(Field):
    """
    Field for related models.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.children = {k: Field(k, **v) for k, v in kwargs["children"].items()} if "children" in kwargs else None


class IntegerField(Field):
    """
    Field for integer values.
    """
    internal_type = int

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("min_value", None)
        kwargs.setdefault("max_value", None)
        super().__init__(*args, **kwargs)

    def validate_data(self):
        super().validate_data()
        assert self.min_value is None or isinstance(self.min_value, (int, float, Decimal)), self.min_value
        assert self.max_value is None or isinstance(self.max_value, (int, float, Decimal)), self.max_value


class FloatField(IntegerField):
    """
    Field for float values.
    """
    internal_type = float


class DecimalField(IntegerField):
    """
    Field for decimal values.
    """
    internal_type = Decimal

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("max_digits", None)
        kwargs.setdefault("decimal_places", None)
        super().__init__(*args, **kwargs)

    def validate_data(self):
        super().validate_data()
        assert self.max_digits is None or isinstance(self.max_digits, int)
        assert self.decimal_places is None or isinstance(self.decimal_places, int)


class StringField(Field):
    """
    Field for string values.
    """
    internal_type = str

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("max_length", None)
        super().__init__(*args, **kwargs)

    def validate_data(self):
        super().validate_data()
        assert self.max_length is None or isinstance(self.max_length, int)


class ChoiceField(StringField):
    """
    Field for choices.
    """
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("choices", [])
        super().__init__(*args, **kwargs)

    def validate_data(self):
        super().validate_data()
        assert isinstance(self.choices, list)


class DateField(Field):
    """
    Field for date values.
    """
    internal_type = date


class DatetimeField(DateField):
    """
    Field for datetime values.
    """
    internal_type = datetime


class BooleanField(Field):
    """
    Field for boolean values.
    """
    internal_type = bool


class ImageField(StringField):
    """
    Field for image uploads.
    """
    pass


class URLField(StringField):
    """
    Field for URL values.
    """
    pass


class EmailField(StringField):
    """
    Field for email values.
    """
    pass


class Undefined:
    """
    Class representing an undefined value.
    """
    def __str__(self):
        return repr(self)

    def __repr__(self):
        return "<Undefined>"

    def __bool__(self):
        return False

    def __eq__(self, other):
        return isinstance(other, Undefined) or other is None

    def __ne__(self, other):
        return not isinstance(other, Undefined) and other is not None


field_mapping: Dict[str, Field] = {
    FIELD: Field,
    INTEGER: IntegerField,
    FLOAT: FloatField,
    DECIMAL: DecimalField,
    STRING: StringField,
    CHOICE: ChoiceField,
    DATE: DateField,
    DATETIME: DatetimeField,
    BOOLEAN: BooleanField,
    RELATED: RelatedField,
    IMAGE: ImageField,
    URL: URLField,
    EMAIL: EmailField,
}
