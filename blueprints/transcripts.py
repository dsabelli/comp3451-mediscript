from collections import OrderedDict
from datetime import datetime
from flask import Blueprint, current_app, render_template, jsonify, request

from models.transcripts import get_all_transcripts, get_transcript, save_transcript

transcript_bp = Blueprint("transcripts", __name__, url_prefix="/transcripts")


@transcript_bp.route("/")
def transcript():
    return render_template("transcripts/transcript.html")


@transcript_bp.route("/archive")
def archive():
    transcripts = get_all_transcripts()
    return render_template("transcripts/archive.html", transcripts=transcripts)


# API endpoint to save transcript
@transcript_bp.route("/save", methods=["POST"])
def save_transcript_endpoint():
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
    transcript = get_transcript(transcript_id)
    if not transcript:
        return "Transcript not found", 404
    return render_template("transcripts/view_transcript.html", transcript=transcript)
