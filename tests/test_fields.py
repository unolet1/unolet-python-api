import unittest
from unolet.fields import (
    Field,
    IntegerField,
    DecimalField,
    StringField,
    ChoiceField,
    DateField,
    DatetimeField,
    BooleanField,
    Undefined,
    FIELD,
    RELATED,
    STRING,
    DATETIME,
    DATE,
    INTEGER,
    FLOAT,
    DECIMAL,
    BOOLEAN,
)


class TestFields(unittest.TestCase):
    def setUp(self):
        return super().setUp()

    def test_field_init(self):
        data = {"type": FIELD, "required": True, "read_only": False}
        field = Field("test_field", **data)
        self.assertEqual(field.name, "test_field")
        self.assertEqual(field.type, FIELD)
        self.assertTrue(field.required)
        self.assertFalse(field.read_only)
        self.assertEqual(field.help_text, "")
        self.assertEqual(field.label, "Test field")

    def test_integer_field_init(self):
        data = {"type": INTEGER, "required": True, "read_only": False}
        integer_field = IntegerField("integer_field", **data)
        self.assertEqual(integer_field.min_value, None)
        self.assertEqual(integer_field.max_value, None)

        data_with_limits = {"type": INTEGER, "required": True, "read_only": False, "min_value": 0, "max_value": 100}
        integer_field_with_limits = IntegerField("integer_field_with_limits", **data_with_limits)
        self.assertEqual(integer_field_with_limits.min_value, 0)
        self.assertEqual(integer_field_with_limits.max_value, 100)

    def test_decimal_field_init(self):
        data = {"type": DECIMAL, "required": True, "read_only": False}
        decimal_field = DecimalField("decimal_field", **data)
        self.assertEqual(decimal_field.decimal_places, None)
        self.assertEqual(decimal_field.max_digits, None)

        data_with_limits = {"type": DECIMAL, "required": True, "read_only": False, "decimal_places": 2, "max_digits": 17}
        decimal_field_with_limits = DecimalField("decimal_field_with_limits", **data_with_limits)
        self.assertEqual(decimal_field_with_limits.decimal_places, 2)
        self.assertEqual(decimal_field_with_limits.max_digits, 17)

    def test_string_field_init(self):
        data = {"type": STRING, "required": True, "read_only": False}
        string_field = StringField("string_field", **data)
        self.assertEqual(string_field.max_length, None)

        data_with_limits = {"type": STRING, "required": True, "read_only": False, "max_length": 100}
        string_field_with_limits = StringField("string_field_with_limits", **data_with_limits)
        self.assertEqual(string_field_with_limits.max_length, 100)


if __name__ == "__main__":
    unittest.main()
