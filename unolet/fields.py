from datetime import date, datetime
from decimal import Decimal


class Field:
    internal_type = None

    def __init__(self, name: str, data: dict):
        self.name = name
        self.type = data["type"]
        self.required = data["required"]
        self.read_only = data["read_only"]
        self.help_text = data.get("help_text", "")
        self.label = data.get("label", name.replace("_", " ").capitalize())

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.name}>"


class RelatedField(Field):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.children = {k:Field(k, v) for k,v in kwargs["children"].items()} if "children" in kwargs else None


class ObjectField(Field):
    internal_type = object

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class IntegerField(Field):
    internal_type = int

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.min_value = kwargs.get("min_value", None)
        self.max_value = kwargs.get("max_value", None)


class FloatField(IntegerField):
    internal_type = float


class DecimalField(IntegerField):
    internal_type = Decimal

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_digits = kwargs.get("max_digits", None)
        self.decimal_places = kwargs.get("decimal_places", None)


class StringField(Field):
    internal_type = str

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_length = kwargs.get("max_length", None)


class ChoiceField(StringField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.choices = kwargs.get("choices", [])


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


field_mapping = {
    'field': Field,
    'integer': IntegerField,
    'float': FloatField,
    'decimal': DecimalField,
    'string': StringField,
    'choice': ChoiceField,
    'date': DateField,
    'datetime': DatetimeField,
    'boolean': BooleanField,
    'related': RelatedField,
    'object': ObjectField,
}