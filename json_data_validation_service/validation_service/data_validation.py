import json
import os

from validate_resource_types import ResourceTypeValidator
from category import Category

class DataValidationService:

    def __init__(self,json_sample_data, resource_type_config=None,
                 patient_schema=None,encounter_schema=None,
                 address_schema=None, phone_schema=None
                 ):
        self.json_sample_data = json_sample_data
        self.resource_type_config = resource_type_config
        self.patient_schema = self.convert_schema_field_types(patient_schema)
        self.encounter_schema = self.convert_schema_field_types(encounter_schema)
        self.address_schema = self.convert_schema_field_types(address_schema)
        self.phone_schema = self.convert_schema_field_types(phone_schema)

    def convert_schema_field_types(self, schema):
        """Convert the string representation of types in the schema to actual Python types."""
        type_mapping = {
            "string": str,
            "int": int,
            "float": float,
            "bool": bool,
            "object": dict
        }

        def process_schema_field(field_rules):
            """Process individual field rules, including nested fields."""
            # Convert the type to the actual Python type
            field_rules["type"] = type_mapping.get(field_rules.get("type", "string"),
                                                   str)  # Default to str if type not found

            if field_rules["type"] == dict and "properties" in field_rules:
                # Process nested fields
                field_rules["properties"] = self.convert_schema_field_types(field_rules["properties"])

        # Convert types in the main schema
        for field, rules in schema.items():
            process_schema_field(rules)

        return schema

    def validate_individual_data(self, json_data):
        errors = []

        # Define a dictionary mapping each section to its corresponding schema
        section_mapping = {
            Category.PATIENT.value: self.patient_schema,
            Category.ENCOUNTER.value: self.encounter_schema,
            Category.PATIENT_ADDRESS.value: self.address_schema,
            Category.PATIENT_PHONE.value: self.phone_schema
        }

        def validate_fields(json_section, schema, section_name):
            """Helper function to validate required fields in a given JSON section."""
            if not json_section:  # Skip if section is None or empty
                return
            required_fields = [field for field, attributes in schema.items() if attributes['required']]
            errors.extend(
                f"Missing {section_name} required field: {field}"
                for field in required_fields
                for each_item in json_section
                if field not in each_item
            )

        # Loop through each section and validate
        for category, schema in section_mapping.items():
            if category == Category.PATIENT.value and Category.PATIENT.value in json_data:
                validate_fields(json_data[Category.PATIENT.value], schema, category)
            elif category == Category.ENCOUNTER.value and Category.ENCOUNTER.value in json_data:
                validate_fields(json_data[Category.ENCOUNTER.value], schema, category)
            else:
                # Validate nested sections like PatientAddress and PatientPhone
                if Category.PATIENT.value in json_data:
                    nested_section = json_data[Category.PATIENT.value][0].get(category)
                    if nested_section is None:
                        errors.append(f"{category} is null.")
                    else:
                        validate_fields(nested_section, schema, category)

        return errors

    #when use this json validation service, here is how you can call it from your program
    def json_validation(address_schema, encounter_schema, json_sample_data, patient_schema, resource_type_config):
        # Validate the Resource Type
        validator_resource_type_service = ResourceTypeValidator(resource_type_config)
        try:
            validation_resource_type_result = validator_resource_type_service.validate_json(json_sample_data)

            # If resource type validation is successful, proceed to schema validation
            if validation_resource_type_result["status"] == "success":
                print("Resource type validation passed.")
                print(validation_resource_type_result["message"])

                # Call  with the loaded JSON data and schemas
                validate_json_data_against_schema(json_sample_data)
            else:
                # If resource type validation fails, raise an error
                print(f"Resource type validation failed: {validation_resource_type_result['message']}")
                raise ValueError(f"Resource type validation failed: {validation_resource_type_result['message']}")

        except Exception as e:
            print(f"An error occurred during resource type validation: {str(e)}")


def load_json_schema_data_from_file(schema_file_path):
    try:
        with open(schema_file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        raise Exception(f"Error loading JSON file: {str(e)}")


def validate_json_data_against_schema(json_sample_data):
    """Validate the JSON data against the provided schemas and return result and error message."""
    # Get the current working directory
    current_directory = os.getcwd()

    # Combine current directory with the file names to form the full paths
    json_sample_file_path = os.path.join(current_directory, '../sample_data/sample.json')
    resource_type_config_file_path = os.path.join(current_directory, '../schema/resource-type-config.json')
    patient_schema_file = os.path.join(current_directory, '../schema/patient-config-schema.json')
    encounter_schema_file = os.path.join(current_directory, '../schema/encounter-schema-config.json')
    address_schema_file = os.path.join(current_directory, '../schema/patient-address-schema-config.json')
    phone_schema_file = os.path.join(current_directory, '../schema/patient-phone-config-schema.json')

    resource_type_config = load_json_schema_data_from_file(resource_type_config_file_path)
    patient_schema = load_json_schema_data_from_file(patient_schema_file)
    encounter_schema = load_json_schema_data_from_file(encounter_schema_file)
    address_schema = load_json_schema_data_from_file(address_schema_file)
    phone_schema = load_json_schema_data_from_file(phone_schema_file)

    # Initialize the validation services
    validator = DataValidationService(json_sample_data,
                                      resource_type_config=resource_type_config,
                                      patient_schema=patient_schema,
                                      encounter_schema=encounter_schema,
                                      address_schema=address_schema,
                                      phone_schema=phone_schema
                                      )

    resource_type_validator = ResourceTypeValidator(resource_type_config)

    try:
        # Validate resource types
        resource_validation_result = resource_type_validator.validate_json(json_sample_data)

        if resource_validation_result["status"] == "failed":
            return {"status": "failed", "message": "Resource type validation failed."}

        # Validate the JSON data against schemas
        validation_errors = validator.validate_individual_data(json_sample_data)

        # Check if there are validation errors
        if validation_errors:
            return {"status": "failed",
                    "message": "Validation failed with the following errors: " + "; ".join(validation_errors)}
        else:
            return {"status": "success", "message": "JSON is valid against the schema."}

    except Exception as e:
        # Return the exception message as part of the error
        return {"status": "failed", "message": f"An error occurred: {str(e)}"}

