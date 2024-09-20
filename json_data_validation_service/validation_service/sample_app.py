import json
import os
from data_validation import validate_json_data_against_schema


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
    json_input_file_path = os.path.join(current_directory, '../input_data/input.json')

    json_input_data = load_json_data_from_file(json_input_file_path)

    results = validate_json_data_against_schema(json_input_data)
    print(results)
# Entry point
if __name__ == "__main__":
    main()
