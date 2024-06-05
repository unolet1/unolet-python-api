import unittest
from unittest.mock import MagicMock

import unolet
from unolet.models import UnoletResource


class TestUnoletResource(unittest.TestCase):

    def setUp(self):
        self.valid_json_response = {
            "id": 1,
            "name": "Resource Name",
            "description": "Resource Description",
            "actions": {
                "POST": {
                    "field1": {"type": "string", "required": True, "read_only": False},
                    "field2": {"type": "integer", "required": False, "read_only": False}
                }
            }
        }
        self.mock_options_response = MagicMock()
        self.mock_options_response.status_code = 200
        self.mock_options_response.json.return_value = self.valid_json_response

        unolet.Unolet.connect("test-token", "http://localhost:8000")

        UnoletResource._options = MagicMock(return_value=self.mock_options_response)
        UnoletResource._endpoint = "test"

    def test_resource_initialization(self):
        resource = UnoletResource(name="Test Resource", field1="Value", field2=123)
        self.assertEqual(resource.field1, "Value")
        self.assertEqual(resource.name, "Test Resource")
        self.assertEqual(resource.field2, 123)

    def test_resource_creation(self):
        UnoletResource._post = MagicMock(return_value=self.mock_options_response)
        resource = UnoletResource.create({"name": "Test Resource", "field1": "Value", "field2": 123})
        self.assertIsInstance(resource, UnoletResource)
        self.assertEqual(resource.name, "Resource Name")
        self.assertEqual(resource.id, 1)

    def test_resource_serialization(self):
        resource = UnoletResource(name="Test Resource", field1="Value", field2=123)
        serialized_data = resource._serialize()
        self.assertEqual(serialized_data, {"name": "Test Resource", "field1": "Value", "field2": 123})


if __name__ == '__main__':
    unittest.main()
