# json_validator.py

import json
import os
from datetime import datetime


def validate_field(field_value, field_schema, field_name):
    expected_type = field_schema.get('type')

    if field_schema.get('required', False) and (field_value is None or field_value == ''):
        return False, f"Missing required field: {field_name}"

    if field_value is not None:
        if expected_type == 'string' and not isinstance(field_value, str):
            return False, f"Field {field_name} should be a string"
        if expected_type == 'integer' and not isinstance(field_value, int):
            return False, f"Field {field_name} should be an integer"
        if expected_type == 'date' and not validate_date(field_value):
            return False, f"Field {field_name} should be a valid date (YYYY-MM-DD)"
        if expected_type == 'date-time' and not validate_datetime(field_value):
            return False, f"Field {field_name} should be a valid date-time (YYYY-MM-DDTHH:MM:SS)"

    return True, None


def validate_date(date_str):
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False


def validate_datetime(datetime_str):
    try:
        datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S')
        return True
    except ValueError:
        return False


def validate_json(data, schema, parent_key=""):
    for key, schema_value in schema.items():
        field_value = data.get(key, None)
        full_key = f"{parent_key}.{key}" if parent_key else key

        if isinstance(schema_value, dict):
            if 'type' in schema_value:
                is_valid, error = validate_field(field_value, schema_value, full_key)
                if not is_valid:
                    return False, error
            else:
                if field_value is not None:
                    is_valid, error = validate_json(field_value, schema_value, full_key)
                    if not is_valid:
                        return False, error
        elif isinstance(schema_value, list) and len(schema_value) > 0:
            if isinstance(field_value, list):
                for item in field_value:
                    is_valid, error = validate_json(item, schema_value[0], full_key)
                    if not is_valid:
                        return False, error
            elif field_value is None and schema_value[0].get('required', False):
                return False, f"Missing required array: {full_key}"

    return True, None


def check_required_attributes(data):
    required_attributes = ['Info', 'Address', 'Identification', 'Email', 'Phone']
    for attr in required_attributes:
        if attr in data and data[attr]:
            return True
    return False


def load_schema(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)


def load_data(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def validate_patient_data( json_input_data):
    # Get the directory of the current file
    current_dir = os.path.dirname(__file__)

    # Construct the relative path to schema.py
    schema_file_path = os.path.join(current_dir, '../schema/patient-config-schema.json')

    # Normalize the path
    schema_file_path = os.path.normpath(schema_file_path)

    schema = load_schema(schema_file_path)

    try:
        if not check_required_attributes(json_input_data['Patient']):
            return "JSON is invalid: At least one of Info, Address, Identification, Email, or Phone is required."

        is_valid, error_message = validate_json(json_input_data, schema)

        if is_valid:
            return "JSON is valid!"
        else:
            return f"JSON is invalid: {error_message}"

    except json.JSONDecodeError:
        return "JSON is invalid: Invalid JSON format."
    except KeyError as e:
        return f"JSON is invalid: Missing required key {str(e)}."
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}."