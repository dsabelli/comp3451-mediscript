# Daniel Sabelli - T00743378 - COMP 3451 Assignment 4

import json
from config import Config


def get_settings():
    """
    Retrieves settings from a JSON file.  If the file doesn't exist or is corrupted,
    it returns default settings and saves them to the file.
    """
    try:
        with open(
            Config.SETTINGS_FILE, "r"
        ) as f:  # Open the settings file in read mode
            return json.load(f)  # Load and return the settings from the JSON file
    except (
        FileNotFoundError,
        json.JSONDecodeError,
    ):  # Handle file not found or JSON decode errors
        # If settings file is corrupted or missing, return defaults
        default_settings = {"theme": "light"}  # Define default settings
        with open(
            Config.SETTINGS_FILE, "w"
        ) as f:  # Open the settings file in write mode
            json.dump(
                default_settings, f, indent=4
            )  # Save the default settings to the file with indentation for readability
        return default_settings  # Return the default settings


def save_settings(settings):
    """
    Saves settings to a JSON file.

    Args:
        settings (dict): The settings to save.

    Returns:
        bool: True if the settings were saved successfully, False otherwise.
    """
    try:
        with open(
            Config.SETTINGS_FILE, "w"
        ) as f:  # Open the settings file in write mode
            json.dump(
                settings, f, indent=4
            )  # Save the settings to the file with indentation
        return True  # Return True to indicate success
    except Exception as e:  # Catch any exceptions that occur during the save operation
        print(f"Error saving settings: {e}")  # Print an error message
        return False  # Return False to indicate failure
