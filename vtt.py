import os
import webbrowser
import whisper
import sounddevice as sd
import soundfile as sf
import numpy as np
from flask import Flask, render_template, request, jsonify
import tempfile

# Flask app setup
app = Flask(__name__)

# Load the Whisper model
model = whisper.load_model("base")

# Function to record external audio
def record_mic_audio(duration=10, sample_rate=44100):
    print(f"🎤 Recording microphone for {duration} seconds...")
    output_file = "mic_audio.wav"
    audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype=np.int16)
    sd.wait()
    sf.write(output_file, audio_data, sample_rate)
    print("✅ Microphone audio recorded.")
    return output_file

# Function to transcribe audio
def transcribe_audio(file_path):
    print("🔄 Transcribing...")
    result = model.transcribe(file_path)
    print(f"✅ Transcription: {result['text']}")
    return result["text"]

# Flask route for transcription
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_audio():
    if "audio" not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files["audio"]

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
        audio_file.save(temp_audio.name)
        temp_audio_path = temp_audio.name

    try:
        transcription = transcribe_audio(temp_audio_path)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        os.remove(temp_audio_path)

    return jsonify({"transcription": transcription})

def main():
    print("\n🎙 Select Input Mode:")
    print("1️⃣ External Microphone (Live Speech)")
    print("2️⃣ Record System Audio from Web App")

    choice = input("Enter 1 or 2: ").strip()

    if choice == "1":
        audio_file = record_mic_audio()
        final_transcription = transcribe_audio(audio_file)

    elif choice == "2":
        print("\n🚀 Opening Web App for System Audio Recording...\n")
        webbrowser.open("http://127.0.0.1:5000/")  # Redirects to the web app

    else:
        print("❌ Invalid choice. Please enter 1 or 2.")
        return

    if choice == "1" and final_transcription:
        print(f"📜 Final Transcription: {final_transcription}")
    elif choice == "1":
        print("❌ Could not generate transcription.")

if __name__ == "__main__":
    main()
