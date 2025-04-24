# Daniel Sabelli - T00743378 - COMP 3451 Assignment 4

from collections import OrderedDict
from datetime import datetime
from flask import Blueprint, current_app, render_template, jsonify, request

from models.transcripts import get_all_transcripts, get_transcript, save_transcript

transcript_bp = Blueprint("transcripts", __name__, url_prefix="/transcripts")


@transcript_bp.route("/")
def transcript():
    """Render the main transcript page."""
    return render_template("transcripts/transcript.html")


@transcript_bp.route("/archive")
def archive():
    """Render the transcript archive page, displaying all saved transcripts."""
    transcripts = get_all_transcripts()
    return render_template("transcripts/archive.html", transcripts=transcripts)


# API endpoint to save transcript
@transcript_bp.route("/save", methods=["POST"])
def save_transcript_endpoint():
    """API endpoint to save a transcript."""
    data = request.json
    title = data.get("title")
    user = data.get("user")

    if not title:
        return jsonify({"error": "Title is required"}), 400
    if not user:
        return jsonify({"error": "User is required"}), 400

    # Get transcript from app config
    original_text = current_app.config.get("CURRENT_TRANSCRIPT", "")
    formatted_text = current_app.config.get("CURRENT_FORMATTED_TRANSCRIPT", "")

    if not original_text or not formatted_text:
        return jsonify({"error": "No transcript available to save"}), 400

    transcript_id = save_transcript(
        title=title,
        user=user,
        original_text=original_text,
        formatted_text=formatted_text,
    )

    return jsonify({"success": True, "id": transcript_id, "title": title, "user": user})


@transcript_bp.route("/view/<transcript_id>")
def view_transcript(transcript_id):
    """Render a page to view a single transcript."""
    transcript = get_transcript(transcript_id)
    if not transcript:
        return "Transcript not found", 404
    return render_template("transcripts/view_transcript.html", transcript=transcript)
