from datetime import date, datetime
from decimal import Decimal
from typing import Dict

from unolet.utils import is_string_decimal, string_to_date


FIELD = "field"
RELATED = "related"
STRING = "string"
INTEGER = "integer"
FLOAT = "float"
DECIMAL = "decimal"
CHOICE = "choice"
DATE = "date"
DATETIME = "datetime"
BOOLEAN = "bool"


class Field:
    internal_type = None

    def __init__(self, name: str, **data):
        self.name = name
        self.type = data.pop("type")
        self.required = data.pop("required")
        self.read_only = data.pop("read_only")
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

    def validate_data(self):
        assert isinstance(self.name, str)
        assert isinstance(self.type, str)
        assert isinstance(self.required, bool)
        assert isinstance(self.read_only, bool)

    def validate_value(self, value):
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
        value = self.validate_value(value)
        if isinstance(value, dict) and 'id' in value:
            pass
        elif isinstance(value, list):
            value = [self.parse_value(e) for e in value]
        elif isinstance(value, str):
            try:
                value = string_to_date(value)
            except ValueError:
                if is_string_decimal(value):
                    value = Decimal(value)
        return value


class RelatedField(Field):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.children = {k:Field(k, v) for k,v in kwargs["children"].items()} if "children" in kwargs else None


class IntegerField(Field):
    internal_type = int

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("min_value", None)
        kwargs.setdefault("max_value", None)
        super().__init__(*args, **kwargs)

    def validate_data(self):
        super().validate_data()
        assert self.min_value is None or isinstance(self.min_value, int)
        assert self.max_value is None or isinstance(self.max_value, int)


class FloatField(IntegerField):
    internal_type = float


class DecimalField(IntegerField):
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
    internal_type = str

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("max_length", None)
        super().__init__(*args, **kwargs)

    def validate_data(self):
        super().validate_data()
        assert self.max_length is None or isinstance(self.max_length, int)


class ChoiceField(StringField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("choices", [])
        super().__init__(*args, **kwargs)

    def validate_data(self):
        super().validate_data()
        assert isinstance(self.choices, list)


class DateField(Field):
    internal_type = date


class DatetimeField(DateField):
    internal_type = datetime


class BooleanField(Field):
    internal_type = bool


class Undefined:
    def __str__(self):
        return repr(self)

    def __repr__(self):
        return f"<Undefined>"

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
}