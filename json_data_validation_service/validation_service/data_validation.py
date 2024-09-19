import json
import os

from validate_resource_types import ResourceTypeValidator

class DataValidationService:

    def __init__(self,json_sample_data, resource_type_config=None, patient_schema=None,encounter_schema=None,address_schema=None):
        self.json_sample_data = json_sample_data
        self.resource_type_config = resource_type_config
        self.patient_schema = self.convert_schema_field_types(patient_schema)
        self.encounter_schema = self.convert_schema_field_types(encounter_schema)
        self.address_schema = self.convert_schema_field_types(address_schema)

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

    def validate_individual_data(self, non_patient_data):
        errors = []
        # Check for required fields
        required_fields = [field for field, attributes in self.patient_schema.items() if attributes['required']]
        for field in required_fields:
            if field not in non_patient_data:
                errors.append(f"Missing field: {field}")

        return errors

    def validate_individual_patient_data(self, json_data):
        errors = []

        # Check for required fields
        if json_data.get('Patient') is not None:
            patient_required_fields = [field for field, attributes in self.patient_schema.items() if attributes['required']]
            for field in patient_required_fields:
                if field not in json_data["Patient"] :
                    errors.append(f"Missing field: {field}")

        if json_data.get('Encounter') is not None:
            patient_required_fields = [field for field, attributes in self.encounter_schema.items() if attributes['required']]
            for field in patient_required_fields:
                if field not in json_data["Encounter"] :
                    errors.append(f"Missing field: {field}")

        # Validate PatientAddress fields
        address_required_fields = [field for field, attributes in self.address_schema.items() if attributes['required']]
        patient = json_data["Patient"]
        # patient_addresses = patient.get('PatientAddress')
        patient_addresses = json_data["Patient"][0]["PatientAddress"]

        if patient_addresses is not None:
            for field in address_required_fields:
                if field not in patient_addresses:
                    errors.append(f"Missing Patient Addresses required field: {field}")

        return errors


    # def validate_all_encounter_in_json(self, json_data):
    #     """Validate all patient entries in the provided JSON data."""
    #     errors = []
    #     data = json_data['Encounter']  # Extract the list of patients
    #
    #     # Validate each patient in the list
    #     for i, enc_data in enumerate(data):
    #         errors = self.validate_individual_encounter_data(enc_data)
    #         if errors:
    #             errors.append(f"Errors for Encounter {i + 1}:")
    #             errors.extend(errors)
    #
    #     return errors

    # def validate_individual_encounter_data(self, patient_data):
    #     en_errors = []
    #
    #     # Check for required fields
    #     required_fields = [field for field, attributes in self.patient_schema.items() if attributes['required']]
    #     for field in required_fields:
    #         if field not in patient_data:
    #             en_errors.append(f"Missing field: {field}")
    #
    #     return en_errors


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
    json_sample_file_path = os.path.join(current_directory, '../sample_data/sample_bad.json')
    resource_type_config_file_path = os.path.join(current_directory, '../schema/resource-type-config.json')
    patient_schema_file = os.path.join(current_directory, '../schema/patient-config-schema.json')
    address_schema_file = os.path.join(current_directory, '../schema/patient-address-schema-config.json')
    encounter_schema_file = os.path.join(current_directory, '../schema/encounter-schema-config.json')

    resource_type_config = load_json_schema_data_from_file(resource_type_config_file_path)
    patient_schema = load_json_schema_data_from_file(patient_schema_file)
    address_schema = load_json_schema_data_from_file(address_schema_file)
    encounter_schema = load_json_schema_data_from_file(encounter_schema_file)

    # Initialize the validation services
    validator = DataValidationService(patient_schema, encounter_schema, address_schema, encounter_schema,
                                      address_schema)
    resource_type_validator = ResourceTypeValidator(resource_type_config)

    try:
        # Validate resource types
        resource_validation_result = resource_type_validator.validate_json(json_sample_data)

        if resource_validation_result["status"] == "failed":
            return {"status": "failed", "message": "Resource type validation failed."}

        # Validate the JSON data against schemas
        validation_errors = validator.validate_individual_patient_data(json_sample_data)
        # Uncomment the next line if encounter validation is also needed
        # validation_errors.extend(validator.validate_all_encounters_in_json(json_sample_data))

        # Check if there are validation errors
        if validation_errors:
            return {"status": "failed",
                    "message": "Validation failed with the following errors: " + "; ".join(validation_errors)}
        else:
            return {"status": "success", "message": "JSON is valid against the schema."}

    except Exception as e:
        # Return the exception message as part of the error
        return {"status": "failed", "message": f"An error occurred: {str(e)}"}

