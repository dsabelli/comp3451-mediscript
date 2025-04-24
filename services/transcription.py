# # services/transcription.py
# import assemblyai as aai
# import threading
# from extensions import socketio
# import asyncio
# from flask import app
# from constants import assemblyai_api_key, prompt_script


# aai.settings.api_key = assemblyai_api_key
# prompt = prompt_script
# transcriber = None
# session_id = None
# transcriber_lock = threading.Lock()


# def on_open(session_opened: aai.RealtimeSessionOpened):
#     global session_id
#     session_id = session_opened.session_id
#     print("Session ID:", session_id)


# def on_data(transcript: aai.RealtimeTranscript):
#     if not transcript.text:
#         return

#     if isinstance(transcript, aai.RealtimeFinalTranscript):
#         socketio.emit("transcript", {"text": transcript.text})
#         asyncio.run(analyze_transcript(transcript.text))
#     else:
#         # Emit the partial transcript to be displayed in real-time
#         socketio.emit("partial_transcript", {"text": transcript.text})


# async def analyze_transcript(transcript):
#     result = aai.Lemur().task(
#         prompt, input_text=transcript, final_model=aai.LemurModel.claude3_5_sonnet
#     )

#     print("Emitting formatted transcript for:", transcript)
#     # Store the transcript and formatted text in session variables
#     app.config["CURRENT_TRANSCRIPT"] = transcript
#     app.config["CURRENT_FORMATTED_TRANSCRIPT"] = result.response

#     socketio.emit("formatted_transcript", {"text": result.response})


# def on_error(error: aai.RealtimeError):
#     print("An error occurred:", error)


# def on_close():
#     global session_id
#     session_id = None
#     print("Closing Session")


# def transcribe_real_time():
#     global transcriber
#     transcriber = aai.RealtimeTranscriber(
#         sample_rate=16_000,
#         on_data=on_data,
#         on_error=on_error,
#         on_open=on_open,
#         on_close=on_close,
#         end_utterance_silence_threshold=5000,
#     )

#     transcriber.connect()

#     microphone_stream = aai.extras.MicrophoneStream(sample_rate=16_000)
#     transcriber.stream(microphone_stream)


# @socketio.on("toggle_transcription")
# def handle_toggle_transcription(data=None):
#     global transcriber, session_id

#     # Add debugging
#     print(f"Received toggle_transcription event with data: {data}")

#     # If data is provided, extract the title
#     transcript_title = (
#         data.get("title", "Untitled Transcript") if data else "Untitled Transcript"
#     )
#     print(f"Toggle transcription with title: {transcript_title}")

#     # Acknowledge receipt of the event
#     socketio.emit(
#         "toggle_transcription_response", {"received": True, "title": transcript_title}
#     )

#     with transcriber_lock:
#         if session_id:
#             if transcriber:
#                 print("Closing transcriber session")
#                 transcriber.close()
#                 transcriber = None
#                 session_id = None
#         else:
#             print("Starting transcriber session")
#             # Store the title in app config
#             app.config["CURRENT_TRANSCRIPT_TITLE"] = transcript_title
#             threading.Thread(target=transcribe_real_time).start()
