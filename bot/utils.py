import os
import json
import uuid # For generating unique IDs
from datetime import datetime

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

def load_tasks():
    """Loads tasks from the DATA_FILE."""
    try:
        with open(DATA_FILE, "r") as f:
            file_content = f.read()
            if file_content:
                return json.loads(file_content)
            return []
    except (FileNotFoundError, json.JSONDecodeError):
        # If file doesn't exist or is corrupt, return an empty list
        ensure_data_file_initialized() # Try to fix it
        return []

def save_tasks(tasks):
    """Saves tasks to the DATA_FILE."""
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(tasks, f, indent=2, ensure_ascii=False) # ensure_ascii=False to support Persian characters
    except Exception as e:
        print(f"Error saving tasks: {e}")

def generate_task_id():
    """Generates a unique ID for a new task."""
    return str(uuid.uuid4()) # Using UUID for robust unique IDs

def get_current_timestamp():
    """Returns the current timestamp in ISO format."""
    return datetime.now().isoformat(timespec='seconds')

def parse_datetime_input(dt_str):
    """
    Parses a datetime string from user input.
    Supports 'YYYY-MM-DD HH:MM' or 'YYYY-MM-DD'.
    Returns datetime object or None if invalid.
    """
    try:
        if 'T' in dt_str: # If user provides full ISO format
            return datetime.fromisoformat(dt_str)
        elif ' ' in dt_str: # If user provides 'YYYY-MM-DD HH:MM'
            return datetime.strptime(dt_str, '%Y-%m-%d %H:%M')
        else: # If user provides 'YYYY-MM-DD'
            return datetime.strptime(dt_str, '%Y-%m-%d')
    except ValueError:
        return None