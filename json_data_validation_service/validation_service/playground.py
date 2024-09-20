import json
from datetime import datetime

# Sample schema
schema = {
    "Patient": {
        "Info": {
            "PatientBk": {
                "type": "string",
                "required": True
            },
            "ActiveInd": {
                "type": "string",
                "required": False
            },
            "PatientId": {
                "type": "string",
                "required": False
            },
            "FirstNm": {
                "type": "string",
                "required": False
            },
            "LastNm": {
                "type": "string",
                "required": False
            },
            "MiddleNm": {
                "type": "string",
                "required": False
            },
            "SuffixNm": {
                "type": "string",
                "required": False
            },
            "BirthTs": {
                "type": "string",
                "required": False,
                "format": "date"
            },
            "MaritalStatus": {
                "type": "string",
                "required": False
            },
            "MultipleBirthInd": {
                "type": "string",
                "required": False
            },
            "BirthOrder": {
                "type": "integer",
                "required": False
            },
            "AdministrativeSex": {
                "type": "string",
                "required": False
            },
            "BirthSex": {
                "type": "string",
                "required": False
            },
            "Race1Cd": {
                "type": "string",
                "required": False
            },
            "Race1Descr": {
                "type": "string",
                "required": False
            },
            "Race2Cd": {
                "type": "string",
                "required": False
            },
            "Race2Descr": {
                "type": "string",
                "required": False
            },
            "Race3Cd": {
                "type": "string",
                "required": False
            },
            "Race3Descr": {
                "type": "string",
                "required": False
            },
            "Ethnicity1Cd": {
                "type": "string",
                "required": False
            },
            "Ethnicity1Descr": {
                "type": "string",
                "required": False
            },
            "Ethnicity2Cd": {
                "type": "string",
                "required": False
            },
            "Ethnicity2Descr": {
                "type": "string",
                "required": False
            },
            "Ethnicity3Cd": {
                "type": "string",
                "required": False
            },
            "Ethnicity3Descr": {
                "type": "string",
                "required": False
            },
            "Language1Cd": {
                "type": "string",
                "required": False
            },
            "Language1Descr": {
                "type": "string",
                "required": False
            },
            "Language1PreferenceInd": {
                "type": "string",
                "required": False
            },
            "Language2Cd": {
                "type": "string",
                "required": False
            },
            "Language2Descr": {
                "type": "string",
                "required": False
            },
            "Language2PreferenceInd": {
                "type": "string",
                "required": False
            },
            "Language3Cd": {
                "type": "string",
                "required": False
            },
            "Language3Descr": {
                "type": "string",
                "required": False
            },
            "Language3PreferenceInd": {
                "type": "string",
                "required": False
            },
            "SourceTransactionNm": {
                "type": "string",
                "required": False
            },
            "SourceTransactionTs": {
                "type": "string",
                "required": False,
                "format": "date-time"
            },
            "ServiceAccountId": {
                "type": "string",
                "required": False
            },
            "TenantNm": {
                "type": "string",
                "required": False
            },
            "SourceNm": {
                "type": "string",
                "required": False
            }
        },
        # Similarly define Address, Identification, Phone, Email fields here
    }
}


# Validation functions
def validate_type(value, expected_type):
    if expected_type == "string":
        return isinstance(value, str)
    elif expected_type == "integer":
        return isinstance(value, int)
    return False


def validate_format(value, expected_format):
    if expected_format == "date":
        try:
            datetime.strptime(value, "%Y-%m-%d")
            return True
        except ValueError:
            return False
    elif expected_format == "date-time":
        try:
            datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")
            return True
        except ValueError:
            return False
    return False


def validate_json(data, schema):
    errors = []

    for field, field_info in schema.items():
        if isinstance(field_info, dict) and "type" in field_info:
            # Field is a simple field
            if field_info["required"] and field not in data:
                errors.append(f"Field '{field}' is required.")
            elif field in data:
                value = data[field]
                if not validate_type(value, field_info["type"]):
                    errors.append(f"Field '{field}' should be of type {field_info['type']}.")
                if "format" in field_info and not validate_format(value, field_info["format"]):
                    errors.append(f"Field '{field}' should follow the format {field_info['format']}.")
        elif isinstance(field_info, dict):
            # Field is an object or array
            if field in data:
                if isinstance(field_info, dict):
                    sub_data = data[field]
                    sub_schema = field_info
                    sub_errors = validate_json(sub_data, sub_schema)
                    errors.extend(sub_errors)

    return errors


# Sample JSON data to validate
data_to_validate = {
    "Patient": {
        "Info": {
            "PatientBk": "BK123",
            "ActiveInd": "Y",
            "PatientId": "123",
            "BirthTs": "2022-01-01"
        }
    }
}

# Run validation
errors = validate_json(data_to_validate["Patient"]["Info"], schema["Patient"]["Info"])

if errors:
    print("Validation errors:")
    for error in errors:
        print(f"- {error}")
else:
    print("Validation passed!")
