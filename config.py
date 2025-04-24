# Daniel Sabelli - T00743378 - COMP 3451 Assignment 4
# config.py
import os, json


class Config:
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "default-dev-key")
    DATA_DIR = "data"
    TRANSCRIPTS_DIR = os.path.join(DATA_DIR, "transcripts")
    USERS_FILE = os.path.join(DATA_DIR, "users.json")
    SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")
    APPOINTMENTS_DIR = os.path.join(DATA_DIR, "appointments")


# Create directories if they don't exist
os.makedirs(Config.TRANSCRIPTS_DIR, exist_ok=True)
os.makedirs(Config.APPOINTMENTS_DIR, exist_ok=True)


# Initialize settings file if it doesn't exist
if not os.path.exists(Config.SETTINGS_FILE):
    default_settings = {"theme": "light"}
    with open(Config.SETTINGS_FILE, "w") as f:
        json.dump(default_settings, f, indent=4)


class Development(Config):
    DEBUG = True


class Production(Config):
    DEBUG = False
