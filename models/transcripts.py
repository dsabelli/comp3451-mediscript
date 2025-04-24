# Daniel Sabelli - T00743378 - COMP 3451 Assignment 4

import os
import json
import time
from datetime import datetime
from config import Config


# File operations for transcripts
def save_transcript(title, user, original_text, formatted_text):
    """Save transcript to a JSON file."""
    # Generate unique ID based on timestamp
    timestamp = int(time.time())  # Get the current timestamp as an integer
    transcript_id = f"{timestamp}"  # Create the transcript ID string

    # Create file path
    file_name = f"{transcript_id}_{title.replace(' ', '_')}.json"  # Create the filename
    file_path = os.path.join(
        Config.TRANSCRIPTS_DIR, file_name
    )  # Create the full file path

    # Create transcript data
    created_at = datetime.now()  # Get the current datetime
    formatted_date = created_at.strftime("%a, %b %d, %Y, %I:%M %p")  # Format the date

    # Create transcript data
    transcript_data = {
        "id": transcript_id,  # Add the transcript ID
        "title": title,  # Add the title
        "original_text": original_text,  # Add the original text
        "formatted_text": formatted_text,  # Add the formatted text
        "user": user,  # Add the user
        "created_at": formatted_date,  # Add the formatted date
        "timestamp": datetime.now().isoformat(),  # Add an ISO format timestamp
    }

    # Save to file
    with open(file_path, "w") as f:  # Open the file in write mode
        json.dump(
            transcript_data, f, indent=2
        )  # Write the JSON data to the file with indentation

    return transcript_id  # Return the transcript ID


def get_transcript(transcript_id):
    """Retrieve a transcript by ID from a JSON file."""
    # Look for file with matching ID
    for filename in os.listdir(
        Config.TRANSCRIPTS_DIR
    ):  # Iterate through files in the transcript directory
        if filename.startswith(
            transcript_id
        ):  # Check if the filename starts with the transcript ID
            file_path = os.path.join(
                Config.TRANSCRIPTS_DIR, filename
            )  # Construct the full file path
            with open(file_path, "r") as f:  # Open the file in read mode
                return json.load(
                    f
                )  # Load and return the transcript data from the JSON file
    return None  # Return None if no matching transcript is found


def get_all_transcripts():
    """Retrieve all transcripts from JSON files."""
    transcripts = []  # Initialize an empty list to store transcripts
    for filename in os.listdir(
        Config.TRANSCRIPTS_DIR
    ):  # Iterate through files in the transcript directory
        if filename.endswith(".json"):  # Check if the file is a JSON file
            file_path = os.path.join(
                Config.TRANSCRIPTS_DIR, filename
            )  # Construct the full file path
            with open(file_path, "r") as f:  # Open the file in read mode
                transcripts.append(
                    json.load(f)
                )  # Load the JSON data and append it to the list

    # Sort by created_at (newest first)
    transcripts.sort(
        key=lambda x: x.get("timestamp", ""), reverse=True
    )  # Sort the transcripts list by timestamp, newest first.
    return transcripts  # Return the list of transcripts
