# utils.py

import os
import json
from datetime import datetime # Import datetime for date parsing

DATA_FILE = "data/tasks.json"

def ensure_data_file_initialized():
    """Ensures the data directory exists and the tasks.json file is initialized."""
    if os.path.dirname(DATA_FILE):
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)

    if not os.path.exists(DATA_FILE) or os.path.getsize(DATA_FILE) == 0:
        with open(DATA_FILE, "w") as f:
            json.dump([], f)
        print(f"Data file '{DATA_FILE}' initialized with empty list.")
    else:
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
        ensure_data_file_initialized()
        return []

def save_tasks(tasks):
    """Saves tasks to the DATA_FILE."""
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(tasks, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving tasks: {e}")

def parse_datetime_input(dt_str):
    """
    Parses a datetime string from user input.
    Supports 'YYYY-MM-DD HH:MM' or 'YYYY-MM-DD'.
    Returns datetime object or None if invalid.
    """
    try:
        if 'T' in dt_str: # If user provides full ISO format (less common for input)
            return datetime.fromisoformat(dt_str)
        elif ' ' in dt_str: # If user provides 'YYYY-MM-DD HH:MM'
            return datetime.strptime(dt_str, '%Y-%m-%d %H:%M')
        else: # If user provides 'YYYY-MM-DD'
            return datetime.strptime(dt_str, '%Y-%m-%d')
    except ValueError:
        return None