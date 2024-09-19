import json
import os
from data_validation import DataValidationService, validate_json_data_against_schema


def load_json_data_from_file(json_file_path):
    """Load the JSON data from the specified file path."""
    try:
        with open(json_file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        raise Exception(f"Error loading JSON file: {str(e)}")


def main():
    # Get the current working directory
    current_directory = os.getcwd()

    # Combine current directory with the file names to form the full paths
    json_sample_file_path = os.path.join(current_directory, '../sample_data/sample_bad.json')
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

    validate_json_data_against_schema(json_sample_data, resource_type_config, patient_schema, encounter_schema,address_schema)
# Entry point
if __name__ == "__main__":
    main()
