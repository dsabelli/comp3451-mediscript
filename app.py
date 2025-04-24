# app.py
from flask import Flask
from extensions import socketio
from blueprints.main import main_bp
from blueprints.transcripts import transcript_bp
from blueprints.appointments import appointment_bp
from blueprints.settings import settings_bp
import config
from models.settings import get_settings


def create_app(config_object=config.Development):
    app = Flask(__name__)
    app.config.from_object(config_object)

    # Initialize extensions
    socketio.init_app(app)

    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(transcript_bp)
    app.register_blueprint(appointment_bp)
    app.register_blueprint(settings_bp)

    @app.context_processor
    def inject_settings():
        settings_data = get_settings()
        return dict(theme=settings_data.get("theme", "light"))

    return app


app = create_app()


import assemblyai as aai
import threading
from extensions import socketio
import asyncio
from constants import assemblyai_api_key, prompt_script


aai.settings.api_key = assemblyai_api_key
prompt = prompt_script
transcriber = None
session_id = None
final_transcript = ""
transcriber_lock = threading.Lock()


def on_open(session_opened: aai.RealtimeSessionOpened):
    global session_id
    session_id = session_opened.session_id
    print("Session ID:", session_id)


def on_data(transcript: aai.RealtimeTranscript):
    global final_transcript
    if not transcript.text:
        return

    if isinstance(transcript, aai.RealtimeFinalTranscript):
        final_transcript += transcript.text
        socketio.emit("transcript", {"text": transcript.text})
        # asyncio.run(analyze_transcript(transcript.text))
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
    global final_transcript
    final_transcript = ""


def on_error(error: aai.RealtimeError):
    print("An error occurred:", error)


def on_close():
    global session_id
    session_id = None
    print("Closing Session")


def transcribe_real_time():
    global transcriber
    transcriber = aai.RealtimeTranscriber(
        sample_rate=48_000,
        on_data=on_data,
        on_error=on_error,
        on_open=on_open,
        on_close=on_close,
        end_utterance_silence_threshold=20000,
    )

    transcriber.connect()

    microphone_stream = aai.extras.MicrophoneStream(sample_rate=48_000)
    transcriber.stream(microphone_stream)


@socketio.on("save_transcript")
def clear_final_transcript():
    global final_transcript
    asyncio.run(analyze_transcript(final_transcript))


@socketio.on("toggle_transcription")
def handle_toggle_transcription(data=None):
    global transcriber, session_id

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
