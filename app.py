from flask import Flask, redirect, render_template, request, jsonify, url_for
from flask_socketio import SocketIO, emit
import assemblyai as aai
import threading
import asyncio
import os
import json
import time
from datetime import datetime, timedelta


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


from flask import render_template
from collections import OrderedDict
from datetime import datetime


@app.route("/appointments")
def appointments():
    # Fetch appointments from your database
    appointments = get_all_appointments()  # Your existing function

    # Group appointments by month
    appointments_by_month = {}

    for appointment in appointments:
        # Parse the date from your appointment
        # Using dictionary access instead of attribute access
        date_str = appointment["date"]  # Change this line
        date_obj = datetime.strptime(date_str, "%a, %b %d, %Y, %I:%M %p")
        month_year = date_obj.strftime("%B %Y")  # "April 2025"

        if month_year not in appointments_by_month:
            appointments_by_month[month_year] = []

        appointments_by_month[month_year].append(appointment)

    # Sort the months chronologically
    sorted_appointments = OrderedDict()

    # Get list of (month_year, date_obj) tuples for sorting
    month_dates = []
    for month_year in appointments_by_month:
        # Extract first date of month for sorting
        first_date = datetime.strptime(month_year, "%B %Y")
        month_dates.append((month_year, first_date))

    # Sort by date
    sorted_month_dates = sorted(month_dates, key=lambda x: x[1])

    # Create ordered dictionary
    for month_year, _ in sorted_month_dates:
        sorted_appointments[month_year] = appointments_by_month[month_year]

    return render_template(
        "appointments.html", appointments_by_month=sorted_appointments
    )


# File operations for appointments
def save_appointment(title, date, description, user):
    """Save appointment to a JSON file"""
    # Generate unique ID based on timestamp
    timestamp = int(time.time())
    appointment_id = f"{timestamp}"

    # Create file path
    file_name = f"{appointment_id}.json"
    file_path = os.path.join(APPOINTMENTS_DIR, file_name)

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
    file_path = os.path.join(APPOINTMENTS_DIR, f"{appointment_id}.json")
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return json.load(f)
    return None


def get_all_appointments():
    """Retrieve all appointments"""
    appointments = []
    for filename in os.listdir(APPOINTMENTS_DIR):
        if filename.endswith(".json"):
            file_path = os.path.join(APPOINTMENTS_DIR, filename)
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


# Add these at the top of your file with other constants
APPOINTMENTS_DIR = os.path.join(DATA_DIR, "appointments")
os.makedirs(APPOINTMENTS_DIR, exist_ok=True)


# API endpoint to save appointment
@app.route("/save-appointment", methods=["POST"])
def save_appointment_endpoint():
    data = request.json
    title = data.get("title")
    date = data.get("date")
    description = data.get("description", "")
    user = data.get("user")

    if not title:
        return jsonify({"error": "Title is required"}), 400
    if not date:
        return jsonify({"error": "Date is required"}), 400
    if not user:
        return jsonify({"error": "User is required"}), 400

    appointment_id = save_appointment(
        title=title, date=date, description=description, user=user
    )

    return jsonify(
        {
            "success": True,
            "id": appointment_id,
            "title": title,
            "date": date,
            "description": description,
            "user": user,
        }
    )


@app.route("/view-appointment/<appointment_id>")
def view_appointment(appointment_id):
    appointment = get_appointment(appointment_id)
    if not appointment:
        return "Appointment not found", 404
    return render_template("view_appointment.html", appointment=appointment)


def delete_appointment(appointment_id):
    """Delete an appointment by ID"""
    file_path = os.path.join(APPOINTMENTS_DIR, f"{appointment_id}.json")
    if os.path.exists(file_path):
        os.remove(file_path)
        return True
    return False


@app.route("/delete-appointment/<appointment_id>", methods=["DELETE"])
def delete_appointment_endpoint(appointment_id):
    success = delete_appointment(appointment_id)
    if success:
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "error": "Appointment not found"}), 404


def update_appointment(appointment_id, title, date, description, user):
    """Update an existing appointment"""
    file_path = os.path.join(APPOINTMENTS_DIR, f"{appointment_id}.json")

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


@app.route("/update-appointment/<appointment_id>", methods=["PUT"])
def update_appointment_endpoint(appointment_id):
    data = request.json
    title = data.get("title")
    date = data.get("date")
    description = data.get("description", "")
    user = data.get("user")

    if not title:
        return jsonify({"error": "Title is required"}), 400
    if not date:
        return jsonify({"error": "Date is required"}), 400
    if not user:
        return jsonify({"error": "User is required"}), 400

    success, result = update_appointment(
        appointment_id=appointment_id,
        title=title,
        date=date,
        description=description,
        user=user,
    )

    if success:
        return jsonify({"success": True, "appointment": result})
    else:
        return jsonify({"success": False, "error": result}), 404


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
