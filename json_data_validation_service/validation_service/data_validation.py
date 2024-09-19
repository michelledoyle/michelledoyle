import json
from validate_resource_types import ResourceTypeValidator

class DataValidationService:

    def __init__(self,json_sample_data, resource_type_config, patient_schema, encounter_schema,address_schema):
        self.json_sample_data = json_sample_data
        self.resource_type_config = resource_type_config
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

    def validate_individual_patient_data(self, patient_data):
        errors = []

        # Check for required fields
        patient_required_fields = [field for field, attributes in self.patient_schema.items() if attributes['required']]
        for field in patient_required_fields:
            if field not in patient_data:
                errors.append(f"Missing field: {field}")

        # Validate PatientAddress fields
        address_required_fields = [field for field, attributes in self.address_schema.items() if attributes['required']]
        address = patient_data.get('PatientAddress', {})
        for field in address_required_fields:
            if field not in address:
                errors.append(f"Missing address field: {field}")

        # encounter_required_fields = [field for field, attributes in self.encounter_schema.items() if attributes['required']]
        # address = patient_data.get('PatientAddress', {})
        # for field in encounter_required_fields:
        #     if field not in address:
        #         errors.append(f"Missing address field: {field}")

        # # Validate PatientPhone if present
        # if 'PatientPhone' in patient_data:
        #     for phone in patient_data['PatientPhone']:
        #         if not isinstance(phone, dict):
        #             errors.append("Invalid format in PatientPhone")
        #         else:
        #             required_phone_fields = ['PhoneID', 'PhoneNumber', 'PhoneType']
        #             for field in required_phone_fields:
        #                 if field not in phone:
        #                     errors.append(f"Missing phone field: {field}")

        return errors

    # def validate_individual_patient_data(self, patient_data):
    #     """Validate individual patient data using the patient schema."""
    #     return self.validate_data_against_schema(patient_data, self.patient_schema)

    def validate_all_patients_in_json(self, json_data):
        """Validate all patient entries in the provided JSON data."""
        errors = []
        patients = json_data['Patient']  # Extract the list of patients

        # Validate each patient in the list
        for i, patient_data in enumerate(patients):
            patient_errors = self.validate_individual_patient_data(patient_data)
            if patient_errors:
                errors.append(f"Errors for Patient {i + 1}:")
                errors.extend(patient_errors)

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
                validate_json_data_against_schema(json_sample_data, patient_schema, encounter_schema)
            else:
                # If resource type validation fails, raise an error
                print(f"Resource type validation failed: {validation_resource_type_result['message']}")
                raise ValueError(f"Resource type validation failed: {validation_resource_type_result['message']}")

        except Exception as e:
            print(f"An error occurred during resource type validation: {str(e)}")




def validate_json_data_against_schema(json_sample_data, resource_type_config, patient_schema, encounter_schema,address_schema):
    """Validate the JSON data against the provided schemas."""
    # Initialize the validation service
    validator = DataValidationService(json_sample_data, resource_type_config, patient_schema, encounter_schema,address_schema)

    # Validate the JSON data
    try:
        validation_errors = validator.validate_all_patients_in_json(json_sample_data)

        # Output validation results
        if validation_errors:
            print("Validation failed with the following errors:")
            for error in validation_errors:
                print(f"- {error}")
        else:
            print("JSON is valid against the schema.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

