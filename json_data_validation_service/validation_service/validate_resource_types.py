import json

class ResourceTypeValidator:

    def __init__(self, schema):
        self.schema = schema

        if not isinstance(self.schema, dict):
            raise TypeError("Schema must be a JSON object (dictionary)")

    def validate_resource_types(self, input_json):
        """Validate that at least one of the resource types in the schema exists in the input JSON."""
        # Get the list of expected resource types from the schema
        schema_resource_types = self.schema.get("resource_type", [])
        input_keys = set(input_json.keys())

        # Check if at least one schema resource type is present in the input JSON data
        if any(resource in input_keys for resource in schema_resource_types):
            return {"status": "success", "message": "At least one required resource type is present in the JSON."}
        else:
            return {"status": "failed", "message": "None of the required resource types are present in the JSON."}

    def validate_json(self, input_json):
        """Validate the input JSON based on resource types."""
        # Validate resource types in the input JSON
        validation_result = self.validate_resource_types(input_json)
        return validation_result
