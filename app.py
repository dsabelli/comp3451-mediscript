from flask import Flask, redirect, render_template, request, jsonify, url_for
from flask_socketio import SocketIO, emit
import assemblyai as aai
import threading
import asyncio
import os
import json
import time
from datetime import datetime


from constant import assemblyai_api_key

app = Flask(__name__)
socketio = SocketIO(app)

aai.settings.api_key = assemblyai_api_key
transcriber = None
session_id = None
transcriber_lock = threading.Lock()
# File storage paths
DATA_DIR = "data"
TRANSCRIPTS_DIR = os.path.join(DATA_DIR, "transcripts")
USERS_FILE = os.path.join(DATA_DIR, "users.json")

# Create directories if they don't exist
os.makedirs(TRANSCRIPTS_DIR, exist_ok=True)

# Initialize users file if it doesn't exist
if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, "w") as f:
        json.dump([], f)


prompt = """You are a medical transcript analyzer. Your task is to process medical transcripts following these guidelines:

1. SPEAKER IDENTIFICATION:
   - Clearly label each speaker (e.g., "Dr. Smith:", "Patient:", "Nurse:") at the beginning of their dialogue
   - Maintain consistent labeling throughout the transcript

2. TEXT FORMATTING:
   Apply formatting to words/phrases that fit into the following categories:
   - Protected Health Information (PHI): Change the font color to red using <span style="color: red;">...</span>
     Examples: patient names, ages, nationalities, gender identities, organizations
   - Medical Condition/History: Bold the text using <strong>...</strong>
     Examples: illnesses, diseases, symptoms, or conditions
   - Anatomy: Italicize the text using <em>...</em>
     Examples: body parts or anatomical locations
   - Medication: Bold the text using <strong>...</strong>
     Examples: prescribed drugs, over-the-counter medications, vitamins, supplements
   - Tests, Treatments, & Procedures: Bold the text using <strong>...</strong>
     Examples: medical tests, treatments, procedures performed or recommended

3. SUMMARY CREATION:
   After the formatted transcript, create a bulleted summary section with these categories:
   - Key Diagnoses: List all diagnosed conditions mentioned
   - Medications: List all medications discussed (current, new, or discontinued)
   - Patient Instructions: Summarize any instructions given to the patient
   - Follow-up Plans: Note any scheduled appointments or recommended follow-ups

Process the transcript by:
1. Using AssemblyAI's detected entities as a starting point for formatting
2. Identifying and formatting any additional relevant items not detected by the AI
3. Creating the comprehensive summary section
4. Returning the formatted transcript with the summary section

Maintain the original flow and meaning of the transcript while applying these enhancements.
"""


# File operations for transcripts
def save_transcript(title, user, original_text, formatted_text):
    """Save transcript to a text file"""
    # Generate unique ID based on timestamp
    timestamp = int(time.time())
    transcript_id = f"{timestamp}"

    # Create file path
    file_name = f"{transcript_id}_{title.replace(' ', '_')}.json"
    file_path = os.path.join(TRANSCRIPTS_DIR, file_name)

    # Create transcript data
    transcript_data = {
        "id": transcript_id,
        "title": title,
        "original_text": original_text,
        "formatted_text": formatted_text,
        "user": user,
        "created_at": datetime.now().isoformat(),
    }

    # Save to file
    with open(file_path, "w") as f:
        json.dump(transcript_data, f, indent=2)

    return transcript_id


def get_transcript(transcript_id):
    """Retrieve a transcript by ID"""
    # Look for file with matching ID
    for filename in os.listdir(TRANSCRIPTS_DIR):
        if filename.startswith(transcript_id):
            file_path = os.path.join(TRANSCRIPTS_DIR, filename)
            with open(file_path, "r") as f:
                return json.load(f)
    return None


def get_all_transcripts():
    """Retrieve all transcripts"""
    transcripts = []
    for filename in os.listdir(TRANSCRIPTS_DIR):
        if filename.endswith(".json"):
            file_path = os.path.join(TRANSCRIPTS_DIR, filename)
            with open(file_path, "r") as f:
                transcripts.append(json.load(f))

    # Sort by created_at (newest first)
    transcripts.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return transcripts


def on_open(session_opened: aai.RealtimeSessionOpened):
    global session_id
    session_id = session_opened.session_id
    print("Session ID:", session_id)


def on_data(transcript: aai.RealtimeTranscript):
    if not transcript.text:
        return

    if isinstance(transcript, aai.RealtimeFinalTranscript):
        socketio.emit("transcript", {"text": transcript.text})
        asyncio.run(analyze_transcript(transcript.text))
    else:
        # Emit the partial transcript to be displayed in real-time
        socketio.emit("partial_transcript", {"text": transcript.text})


async def analyze_transcript(transcript):
    result = aai.Lemur().task(
        prompt, input_text=transcript, final_model=aai.LemurModel.claude3_5_sonnet
    )

    print("Emitting formatted transcript for:", transcript)
    # Store the transcript and formatted text in session variables
    app.config["CURRENT_TRANSCRIPT"] = transcript
    app.config["CURRENT_FORMATTED_TRANSCRIPT"] = result.response

    socketio.emit("formatted_transcript", {"text": result.response})


def on_error(error: aai.RealtimeError):
    print("An error occurred:", error)


def on_close():
    global session_id
    session_id = None
    print("Closing Session")


def transcribe_real_time():
    global transcriber
    transcriber = aai.RealtimeTranscriber(
        sample_rate=16_000,
        on_data=on_data,
        on_error=on_error,
        on_open=on_open,
        on_close=on_close,
        end_utterance_silence_threshold=5000,
    )

    transcriber.connect()

    microphone_stream = aai.extras.MicrophoneStream(sample_rate=16_000)
    transcriber.stream(microphone_stream)


@app.route("/")
def root():
    # Redirect the root URL to the login page
    return redirect(url_for("login"))


@app.route("/home")
def index():
    # This is now your main application page after login
    return render_template("index.html")


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/transcript")
def transcript():
    return render_template("transcript.html")


@app.route("/search")
def search():
    return render_template("search.html")


@app.route("/archive")
def archive():
    transcripts = get_all_transcripts()
    return render_template("archive.html", transcripts=transcripts)


@app.route("/settings")
def settings():
    return render_template("settings.html")


@app.route("/appointments")
def appointments():
    return render_template("appointments.html")


# API endpoint to save transcript
@app.route("/save-transcript", methods=["POST"])
def save_transcript_endpoint():
    data = request.json
    title = data.get("title")
    user = data.get("user")

    if not title:
        return jsonify({"error": "Title is required"}), 400
    if not user:
        return jsonify({"error": "User is required"}), 400

    # Get transcript from app config
    original_text = app.config.get("CURRENT_TRANSCRIPT", "")
    formatted_text = app.config.get("CURRENT_FORMATTED_TRANSCRIPT", "")

    if not original_text or not formatted_text:
        return jsonify({"error": "No transcript available to save"}), 400

    transcript_id = save_transcript(
        title=title,
        user=user,
        original_text=original_text,
        formatted_text=formatted_text,
    )

    return jsonify({"success": True, "id": transcript_id, "title": title, "user": user})


@app.route("/view-transcript/<transcript_id>")
def view_transcript(transcript_id):
    transcript = get_transcript(transcript_id)
    if not transcript:
        return "Transcript not found", 404
    return render_template("view_transcript.html", transcript=transcript)


@socketio.on("toggle_transcription")
def handle_toggle_transcription(data=None):
    global transcriber, session_id

    # If data is provided, extract the title
    transcript_title = (
        data.get("title", "Untitled Transcript") if data else "Untitled Transcript"
    )
    print(f"Toggle transcription with title: {transcript_title}")

    with transcriber_lock:
        if session_id:
            if transcriber:
                print("Closing transcriber session")
                transcriber.close()
                transcriber = None
                session_id = None
        else:
            print("Starting transcriber session")
            # Store the title in app config
            app.config["CURRENT_TRANSCRIPT_TITLE"] = transcript_title

            threading.Thread(target=transcribe_real_time).start()


if __name__ == "__main__":
    socketio.run(app, port=6069, debug=True)
