import json
import os
from validate_resource_types import ResourceTypeValidator

class DataValidationService:

    def __init__(self, patient_schema,encounter_schema,address_schema):
        self.patient_schema = self.convert_schema_field_types(patient_schema)
        self.encounter_schema = self.convert_schema_field_types(encounter_schema)
        self.address_schema = self.convert_schema_field_types(address_schema)

    def convert_schema_field_types(self, schema):
        """Convert the string representation of types in the schema to actual Python types."""
        type_mapping = {
            "str": str,
            "int": int,
            "float": float,
            "bool": bool,
            "object": dict
        }

        def process_schema_field(field_rules):
            """Process individual field rules, including nested fields."""
            # Convert the type to the actual Python type
            field_rules["type"] = type_mapping.get(field_rules.get("type", "str"),
                                                   str)  # Default to str if type not found

            if field_rules["type"] == dict and "properties" in field_rules:
                # Process nested fields
                field_rules["properties"] = self.convert_schema_field_types(field_rules["properties"])

            # Process nested PatientAddress field
            if field_rules.get("type") == "PatientAddress":
                # Treat it as a dictionary of fields
                field_rules["type"] = dict
                if "properties" in field_rules:
                    field_rules["properties"] = self.convert_schema_field_types(field_rules["properties"])

        # Convert types in the main schema
        for field, rules in schema.items():
            process_schema_field(rules)

        return schema

    def load_json_data_from_file(self, json_file_path):
        """Load the JSON data from the specified file path."""
        try:
            with open(json_file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            raise Exception(f"Error loading JSON file: {str(e)}")

    def validate_data_against_schema(self, data, schema, is_address=False):
        """Validate the provided data against the given schema, handling both patient and address data."""
        errors = []
        for field, rules in schema.items():
            # Check if required field is present
            if rules.get("required") and field not in data:
                errors.append(f"Missing required field: {field}")
                continue

            # If field exists, validate its type
            if field in data:
                value = data[field]
                expected_type = rules["type"]
                if not isinstance(value, expected_type):
                    errors.append(
                        f"Field '{field}' has wrong type. Expected {expected_type.__name__}, got {type(value).__name__}")

                # Validate nested objects, including PatientAddress
                if expected_type == dict and "properties" in rules:
                    if field == "PatientAddress" and is_address is False:
                        # Use address schema for PatientAddress validation
                        nested_errors = self.validate_data_against_schema(value, self.address_schema, is_address=True)
                    else:
                        # Validate regular nested objects
                        nested_errors = self.validate_data_against_schema(value, rules["properties"])

                    if nested_errors:
                        errors.append(f"Errors in nested field '{field}':")
                        errors.extend(nested_errors)
        return errors

    def validate_individual_patient_data(self, patient_data):
        """Validate individual patient data using the patient schema."""
        return self.validate_data_against_schema(patient_data, self.patient_schema)

    def validate_all_patients_in_json(self, json_data):
        """Validate all patient entries in the provided JSON data."""
        errors = []

        # # Check if 'Patients' key exists in the root of the JSON
        # if 'Patients' not in json_data:
        #     errors.append("Missing 'Patients' key in the JSON.")
        #     return errors

        patients = json_data['Patients']  # Extract the list of patients

        # Validate each patient in the list
        for i, patient_data in enumerate(patients):
            patient_errors = self.validate_individual_patient_data(patient_data)
            if patient_errors:
                errors.append(f"Errors for Patient {i + 1}:")
                errors.extend(patient_errors)

        return errors


def validate_json_file_against_schema(json_file_path, patient_schema_file, address_schema_file, encounter_schema_file):
    """Load the JSON file and schemas, then validate the JSON data against the schemas."""
    # Load expected schema from the JSON schema files
    with open(patient_schema_file, 'r') as f:
        patient_schema = json.load(f)
    with open(encounter_schema_file, 'r') as f:
        encounter_schema = json.load(f)
    with open(address_schema_file, 'r') as f:
        address_schema = json.load(f)

    # Initialize the validation validation_service
    validator = DataValidationService(patient_schema, encounter_schema, address_schema)

    # Load and validate the JSON data
    try:
        json_data = validator.load_json_data_from_file(json_file_path)
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
    json_file_path = os.path.join(current_directory, './sample_data/sample_bad.json')

    resource_type_config_file_path = os.path.join(current_directory, './schema/resource-type-config.json')
    patient_schema_file = os.path.join(current_directory, './schema/patient-config-schema.json')
    address_schema_file = os.path.join(current_directory, './schema/patient-address-schema-config.json')
    encounter_schema_file = os.path.join(current_directory, './schema/encounter-schema-config.json')

    # Validate the Resource Type first
    # Create an instance of ResourceTypeValidator
    validator_resource_type_service = ResourceTypeValidator(resource_type_config_file_path)

    # Validate the resource types in the JSON file
    validation_resource_type_result, message = validator_resource_type_service.validate_json(json_file_path)

    # If resource type validation is successful, proceed to schema validation
    if validation_resource_type_result:
        print("Resource type validation passed.")
        print(message)

        # Call validate_json_file_against_schema if resource types are valid
        validate_json_file_against_schema(json_file_path, patient_schema_file,
                                          address_schema_file, encounter_schema_file)
    else:
        # If resource type validation fails, raise an error
        print(f"Resource type validation failed: {message}")
        raise ValueError(f"Resource type validation failed: {message}")


# Entry point
if __name__ == "__main__":
    main()
