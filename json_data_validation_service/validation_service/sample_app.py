import json
import os
from data_validation import DataValidationService
from validate_resource_types import ResourceTypeValidator


def load_json_data_from_file(json_file_path):
    """Load the JSON data from the specified file path."""
    try:
        with open(json_file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        raise Exception(f"Error loading JSON file: {str(e)}")


def validate_json_file_against_schema(json_data, patient_schema, address_schema, encounter_schema):
    """Validate the JSON data against the provided schemas."""
    # Initialize the validation service
    validator = DataValidationService(patient_schema, encounter_schema, address_schema)

    # Validate the JSON data
    try:
        validation_errors = validator.validate_all_patients_in_json(json_data)

        # Output validation results
        if validation_errors:
            print("Validation failed with the following errors:")
            for error in validation_errors:
                print(f"- {error}")
        else:
            print("JSON is valid against the schema.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")


def main():
    # Get the current working directory
    current_directory = os.getcwd()

    # Combine current directory with the file names to form the full paths
    json_sample_file_path = os.path.join(current_directory, '../sample_data/sample_good.json')
    resource_type_config_file_path = os.path.join(current_directory, '../schema/resource-type-config.json')
    patient_schema_file = os.path.join(current_directory, '../schema/patient-config-schema.json')
    address_schema_file = os.path.join(current_directory, '../schema/patient-address-schema-config.json')
    encounter_schema_file = os.path.join(current_directory, '../schema/encounter-schema-config.json')

    # Load JSON data and schemas from files
    try:
        json_sample_data = load_json_data_from_file(json_sample_file_path)

        resource_type_config = load_json_data_from_file(resource_type_config_file_path)
        patient_schema = load_json_data_from_file(patient_schema_file)
        address_schema = load_json_data_from_file(address_schema_file)
        encounter_schema = load_json_data_from_file(encounter_schema_file)
    except Exception as e:
        print(f"Error loading files: {str(e)}")
        return

    # Validate the Resource Type
    validator_resource_type_service = ResourceTypeValidator(resource_type_config)

    try:
        validation_resource_type_result = validator_resource_type_service.validate_json(json_sample_data)

        # If resource type validation is successful, proceed to schema validation
        if validation_resource_type_result["status"] == "success":
            print("Resource type validation passed.")
            print(validation_resource_type_result["message"])

            # Call validate_json_file_against_schema with the loaded JSON data and schemas
            validate_json_file_against_schema(
                json_sample_data,
                patient_schema,
                address_schema,
                encounter_schema
            )
        else:
            # If resource type validation fails, raise an error
            print(f"Resource type validation failed: {validation_resource_type_result['message']}")
            raise ValueError(f"Resource type validation failed: {validation_resource_type_result['message']}")

    except Exception as e:
        print(f"An error occurred during resource type validation: {str(e)}")


# Entry point
if __name__ == "__main__":
    main()
