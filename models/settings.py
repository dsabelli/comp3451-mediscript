import json
from config import Config


def get_settings():
    try:
        with open(Config.SETTINGS_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # If settings file is corrupted or missing, return defaults
        default_settings = {"theme": "light"}
        with open(Config.SETTINGS_FILE, "w") as f:
            json.dump(default_settings, f, indent=4)
        return default_settings


def save_settings(settings):
    try:
        with open(Config.SETTINGS_FILE, "w") as f:
            json.dump(settings, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving settings: {e}")
        return False
