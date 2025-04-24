# Daniel Sabelli - T00743378 - COMP 3451 Assignment 4

# app.py
from flask import Flask  # Import the Flask framework
from extensions import socketio  # Import the SocketIO extension
from blueprints.main import main_bp  # Import the main blueprint
from blueprints.transcripts import transcript_bp  # Import the transcript blueprint
from blueprints.appointments import appointment_bp  # Import the appointment blueprint
from blueprints.settings import settings_bp  # Import the settings blueprint
import config  # Import the configuration module
from models.settings import (
    get_settings,
)  # Import the function to get settings from the database


def create_app(config_object=config.Development):
    """
    Creates and configures the Flask application.

    Args:
        config_object: The configuration object to use (default: Development).

    Returns:
        A Flask application instance.
    """
    app = Flask(__name__)  # Create a new Flask application instance
    app.config.from_object(config_object)  # Load configuration from the provided object

    # Initialize extensions
    socketio.init_app(app)  # Initialize the SocketIO extension with the app

    # Register blueprints
    app.register_blueprint(main_bp)  # Register the main blueprint
    app.register_blueprint(transcript_bp)  # Register the transcript blueprint
    app.register_blueprint(appointment_bp)  # Register the appointment blueprint
    app.register_blueprint(settings_bp)  # Register the settings blueprint

    @app.context_processor
    def inject_settings():
        """
        Injects settings into the application context, making them available to templates.
        Specifically, it injects the 'theme' setting.
        """
        settings_data = get_settings()  # Retrieve settings data from the database
        return dict(
            theme=settings_data.get("theme", "light")
        )  # Return a dictionary containing the theme, defaulting to 'light'

    return app  # Return the created Flask application instance


app = create_app()  # Create the Flask application instance


import assemblyai as aai  # Import the AssemblyAI library
import threading  # Import the threading module for handling concurrent tasks
from extensions import socketio  # Import the SocketIO instance from extensions.py
import asyncio
from constants import (
    assemblyai_api_key,
    prompt_script,
)  # Import API key and prompt script


aai.settings.api_key = assemblyai_api_key  # Set the AssemblyAI API key
prompt = prompt_script  # Store the prompt script
transcriber = None  # Initialize the global transcriber object
session_id = None  # Initialize the global session ID
final_transcript = ""
transcriber_lock = threading.Lock()


def on_open(session_opened: aai.RealtimeSessionOpened):
    """
    Callback function called when a Realtime session is opened.

    Args:
        session_opened: The RealtimeSessionOpened object containing session information.
    """
    global session_id
    session_id = session_opened.session_id  # Store the session ID
    print("Session ID:", session_id)  # Print the session ID
    # You could also emit a socketio event here to notify the client


def on_data(transcript: aai.RealtimeTranscript):
    """
    Callback function called when a Realtime transcript is received.  This function
    processes the transcript and emits SocketIO events.

    Args:
        transcript: The RealtimeTranscript object containing the transcribed text.
    """
    global final_transcript
    if not transcript.text:  # Check if the transcript text is empty
        return  # Return if there is no text

    if isinstance(
        transcript, aai.RealtimeFinalTranscript
    ):  # Check if it's a final transcript
        final_transcript += transcript.text
        socketio.emit(
            "transcript", {"text": transcript.text}
        )  # Emit the final transcript text
        # asyncio.run(analyze_transcript(transcript.text)) # Removed direct call to async, handled in save_transcript
    else:
        # Emit the partial transcript to be displayed in real-time
        socketio.emit("partial_transcript", {"text": transcript.text})


async def analyze_transcript(transcript):
    """
    Analyzes the given transcript using AssemblyAI's Lemur API and emits the formatted result.

    Args:
      transcript: The transcript text to analyze.
    """
    result = aai.Lemur().task(
        prompt, input_text=transcript, final_model=aai.LemurModel.claude3_5_sonnet
    )  # Analyze the transcript

    print("Emitting formatted transcript for:", transcript)
    # Store the transcript and formatted text in session variables
    app.config["CURRENT_TRANSCRIPT"] = transcript
    app.config["CURRENT_FORMATTED_TRANSCRIPT"] = result.response

    socketio.emit(
        "formatted_transcript", {"text": result.response}
    )  # Emit the formatted transcript
    global final_transcript
    final_transcript = ""


def on_error(error: aai.RealtimeError):
    """
    Callback function called when a Realtime error occurs.

    Args:
        error: The RealtimeError object containing the error information.
    """
    print("An error occurred:", error)  # Print the error message


def on_close():
    """
    Callback function called when the Realtime session is closed.
    """
    global session_id
    session_id = None  # Reset the session ID
    print("Closing Session")  # Print a message indicating the session is closing


def transcribe_real_time():
    """
    Sets up and starts the real-time transcription process using AssemblyAI.
    """
    global transcriber  # Access the global transcriber variable
    transcriber = aai.RealtimeTranscriber(  # Create a RealtimeTranscriber instance
        sample_rate=48_000,  # Set the sample rate to 48kHz
        on_data=on_data,  # Set the callback function for handling transcript data
        on_error=on_error,  # Set the callback function for handling errors
        on_open=on_open,  # Set the callback function for when the session opens
        on_close=on_close,  # Set the callback function for when the session closes
        end_utterance_silence_threshold=700,
    )

    transcriber.connect()  # Connect to the AssemblyAI Realtime API

    microphone_stream = aai.extras.MicrophoneStream(
        sample_rate=48_000
    )  # Create a microphone stream
    transcriber.stream(
        microphone_stream
    )  # Start streaming audio from the microphone to the transcriber


@socketio.on("save_transcript")
def clear_final_transcript():
    """
    SocketIO event handler for the 'save_transcript' event.  It calls the
    analyze_transcript function with the final transcript.
    """
    global final_transcript
    asyncio.run(analyze_transcript(final_transcript))


@socketio.on("toggle_transcription")
def handle_toggle_transcription(data=None):
    """
    SocketIO event handler for the 'toggle_transcription' event.
    Starts or stops real-time transcription based on the current state.
    """
    global transcriber, session_id  # Access the global transcriber and session_id variables

    # Add debugging
    print(f"Received toggle_transcription event with data: {data}")

    # If data is provided, extract the title
    transcript_title = (
        data.get("title", "Untitled Transcript") if data else "Untitled Transcript"
    )
    print(f"Toggle transcription with title: {transcript_title}")

    # Acknowledge receipt of the event
    socketio.emit(
        "toggle_transcription_response", {"received": True, "title": transcript_title}
    )

    with transcriber_lock:
        if session_id:  # Check if a session is currently active
            if transcriber:
                print(
                    "Closing transcriber session"
                )  # Print a message indicating session closure
                transcriber.close()  # Close the transcriber
                transcriber = None  # Reset the transcriber
                session_id = None  # Clear the session ID
        else:
            print(
                "Starting transcriber session"
            )  # Print a message indicating session start
            # Store the title in app config
            app.config["CURRENT_TRANSCRIPT_TITLE"] = transcript_title
            threading.Thread(
                target=transcribe_real_time
            ).start()  # Start transcription in a new thread


if __name__ == "__main__":
    socketio.run(app, port=6069, debug=True)  # Run the Flask application with SocketIO
