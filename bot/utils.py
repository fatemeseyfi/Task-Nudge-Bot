import os
import json

# Path to the data file
DATA_FILE = "data/tasks.json"

def ensure_data_file_initialized():
    """
    Ensures the data directory exists and the tasks.json file is initialized
    with an empty JSON array if it doesn't exist or is empty/corrupt.
    """
    # Create directory if it doesn't exist (if DATA_FILE includes a path)
    if os.path.dirname(DATA_FILE):
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)

    # If the file doesn't exist or is empty, initialize it with an empty JSON array
    if not os.path.exists(DATA_FILE) or os.path.getsize(DATA_FILE) == 0:
        with open(DATA_FILE, "w") as f:
            json.dump([], f)
        print(f"Data file '{DATA_FILE}' initialized with empty list.")
    else:
        # Optional: Try to load to check if it's valid JSON
        try:
            with open(DATA_FILE, "r") as f:
                json.load(f)
            print(f"Data file '{DATA_FILE}' exists and is valid JSON.")
        except json.JSONDecodeError:
            print(f"Warning: Data file '{DATA_FILE}' exists but is not valid JSON. Re-initializing.")
            with open(DATA_FILE, "w") as f:
                json.dump([], f)
            print(f"Data file '{DATA_FILE}' re-initialized due to corruption.")

# You can add other utility functions here in the future