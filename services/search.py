# Daniel Sabelli - T00743378 - COMP 3451 Assignment 4
import json
import os

from config import Config


def search_transcripts(keyword):
    """Search transcripts for a specific keyword"""
    results = []

    # Convert keyword to lowercase for case-insensitive search
    keyword = keyword.lower()

    for filename in os.listdir(Config.TRANSCRIPTS_DIR):
        if filename.endswith(".json"):
            file_path = os.path.join(Config.TRANSCRIPTS_DIR, filename)
            with open(file_path, "r") as f:
                transcript = json.load(f)

                # Check if keyword is in title or original text
                if (
                    keyword in transcript.get("title", "").lower()
                    or keyword in transcript.get("original_text", "").lower()
                ):
                    results.append(transcript)

    # Sort by created_at (newest first)
    results.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return results
