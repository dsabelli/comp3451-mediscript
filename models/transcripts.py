import os
import json
import time
from datetime import datetime
from collections import OrderedDict

from config import Config


# File operations for transcripts
def save_transcript(title, user, original_text, formatted_text):
    """Save transcript to a text file"""
    # Generate unique ID based on timestamp
    timestamp = int(time.time())
    transcript_id = f"{timestamp}"

    # Create file path
    file_name = f"{transcript_id}_{title.replace(' ', '_')}.json"
    file_path = os.path.join(Config.TRANSCRIPTS_DIR, file_name)

    # Create transcript data
    created_at = datetime.now()
    formatted_date = created_at.strftime("%a, %b %d, %Y, %I:%M %p")  # Format the date

    # Create transcript data
    transcript_data = {
        "id": transcript_id,
        "title": title,
        "original_text": original_text,
        "formatted_text": formatted_text,
        "user": user,
        "created_at": formatted_date,
        "timestamp": datetime.now().isoformat(),
    }

    # Save to file
    with open(file_path, "w") as f:
        json.dump(transcript_data, f, indent=2)

    return transcript_id


def get_transcript(transcript_id):
    """Retrieve a transcript by ID"""
    # Look for file with matching ID
    for filename in os.listdir(Config.TRANSCRIPTS_DIR):
        if filename.startswith(transcript_id):
            file_path = os.path.join(Config.TRANSCRIPTS_DIR, filename)
            with open(file_path, "r") as f:
                return json.load(f)
    return None


def get_all_transcripts():
    """Retrieve all transcripts"""
    transcripts = []
    for filename in os.listdir(Config.TRANSCRIPTS_DIR):
        if filename.endswith(".json"):
            file_path = os.path.join(Config.TRANSCRIPTS_DIR, filename)
            with open(file_path, "r") as f:
                transcripts.append(json.load(f))

    # Sort by created_at (newest first)
    transcripts.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    return transcripts
