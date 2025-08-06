from flask import Flask, render_template, request, jsonify, send_file
import os
import threading
import sounddevice as sd
import soundfile as sf
import numpy as np
import whisper

app = Flask(__name__, static_url_path="/static")

# Load Whisper model
model = whisper.load_model("base")

# Global variables
RECORDING = False
AUDIO_FILE_PATH = "recorded_audio.wav"
SAMPLE_RATE = 44100
CHANNELS = 1

# Function to record system audio
def record_audio():
    global RECORDING
    RECORDING = True
    audio_data = []

    def callback(indata, frames, time, status):
        if RECORDING:
            audio_data.append(indata.copy())

    with sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, callback=callback):
        while RECORDING:
            sd.sleep(100)

    # Save recorded audio
    sf.write(AUDIO_FILE_PATH, np.concatenate(audio_data, axis=0), SAMPLE_RATE)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/start_recording", methods=["POST"])
def start_recording():
    global RECORDING
    if RECORDING:
        return jsonify({"message": "Already recording!"})

    thread = threading.Thread(target=record_audio)
    thread.start()
    return jsonify({"message": "Recording started..."})

@app.route("/stop_recording", methods=["POST"])
def stop_recording():
    global RECORDING
    RECORDING = False

    if os.path.exists(AUDIO_FILE_PATH):
        return jsonify({"file": AUDIO_FILE_PATH})
    else:
        return jsonify({"error": "Recording failed!"}), 500

@app.route("/transcribe", methods=["POST"])
def transcribe():
    file_path = request.json.get("file_path", AUDIO_FILE_PATH)
    
    if not os.path.exists(file_path):
        return jsonify({"error": "File not found!"})

    try:
        result = model.transcribe(file_path)
        transcription = result["text"]

        if not transcription.strip():
            return jsonify({"error": "No voice detected in the audio!"})

        return jsonify({"transcription": transcription})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/upload", methods=["POST"])
def upload_audio():
    if "audio" not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files["audio"]
    temp_audio_path = "uploaded_audio.wav"

    try:
        audio_file.save(temp_audio_path)
        result = model.transcribe(temp_audio_path)

        transcription = result["text"]

        if not transcription.strip():
            return jsonify({"error": "No voice detected in the uploaded audio!"})

        os.remove(temp_audio_path)  # Delete after transcription

        return jsonify({"transcription": transcription})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
