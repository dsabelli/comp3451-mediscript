# Daniel Sabelli - T00743378 - COMP 3451 Assignment 4

import os
import json
import time
from datetime import datetime
from collections import OrderedDict

from config import Config


# File operations for appointments
def save_appointment(title, date, description, user):
    """Save appointment to a JSON file"""
    # Generate unique ID based on timestamp
    timestamp = int(time.time())
    appointment_id = f"{timestamp}"

    # Create file path
    file_name = f"{appointment_id}.json"
    file_path = os.path.join(Config.APPOINTMENTS_DIR, file_name)

    # Create appointment data
    appointment_data = {
        "id": appointment_id,
        "title": title,
        "date": date,
        "description": description,
        "user": user,
        "created_at": datetime.now().isoformat(),
    }

    # Save to file
    with open(file_path, "w") as f:
        json.dump(appointment_data, f, indent=2)

    return appointment_id


def get_appointment(appointment_id):
    """Retrieve an appointment by ID"""
    file_path = os.path.join(Config.APPOINTMENTS_DIR, f"{appointment_id}.json")
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return json.load(f)
    return None


def get_all_appointments():
    """Retrieve all appointments"""
    appointments = []
    for filename in os.listdir(Config.APPOINTMENTS_DIR):
        if filename.endswith(".json"):
            file_path = os.path.join(Config.APPOINTMENTS_DIR, filename)
            with open(file_path, "r") as f:
                appointments.append(json.load(f))

    # Sort by appointment date (upcoming first)
    def get_date_for_sorting(appointment):
        try:
            date_str = appointment.get("date", "")
            if date_str:
                return datetime.strptime(date_str, "%a, %b %d, %Y, %I:%M %p")
            return datetime.max  # For appointments without dates
        except ValueError:
            return datetime.max  # In case of date parsing errors

    appointments.sort(key=get_date_for_sorting)
    return appointments


def delete_appointment(appointment_id):
    """Delete an appointment by ID"""
    file_path = os.path.join(Config.APPOINTMENTS_DIR, f"{appointment_id}.json")
    if os.path.exists(file_path):
        os.remove(file_path)
        return True
    return False


def update_appointment(appointment_id, title, date, description, user):
    """Update an existing appointment"""
    file_path = os.path.join(Config.APPOINTMENTS_DIR, f"{appointment_id}.json")

    if not os.path.exists(file_path):
        return False, "Appointment not found"

    # Get existing appointment data
    with open(file_path, "r") as f:
        appointment_data = json.load(f)

    # Update fields
    appointment_data["title"] = title
    appointment_data["date"] = date
    appointment_data["description"] = description
    appointment_data["user"] = user
    appointment_data["updated_at"] = datetime.now().isoformat()

    # Save updated appointment
    with open(file_path, "w") as f:
        json.dump(appointment_data, f, indent=2)

    return True, appointment_data
