import json

class ResourceTypeValidator:

    def __init__(self, file_path):
        self.schema = self.load_json_data_from_file(file_path)

        if not isinstance(self.schema, dict):
            raise TypeError("Schema must be a JSON object (dictionary)")

    def load_json_data_from_file(self, file_path):
        """Load the JSON data from the specified file path."""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                if not isinstance(data, dict):
                    raise ValueError("JSON file must contain a JSON object (dictionary)")
                return data
        except Exception as e:
            raise Exception(f"Error loading JSON file: {str(e)}")

    def validate_resource_types(self, json_data):
        """Validate that the resource types in the JSON data exist as per the schema."""
        schema_resource_types = self.schema.get("resource_type", [])
        missing_resources = []

        # Check for the presence of each resource type in the JSON data
        for resource in schema_resource_types:
            if resource.capitalize() not in json_data:
                missing_resources.append(resource)

        if missing_resources:
            return {"status": "fail", "message": f"Missing resource types in JSON data: {', '.join(missing_resources)}"}
        else:
            return {"status": "success", "message": "All required resource types are present in the JSON data."}

    def validate_json(self, json_file_path):
        """Validate the JSON file based on resource types."""
        # Load JSON data from the file
        json_data = self.load_json_data_from_file(json_file_path)

        # Validate resource types in the JSON data
        validation_result = self.validate_resource_types(json_data)
        return validation_result
