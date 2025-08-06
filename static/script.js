document.addEventListener("DOMContentLoaded", function () {
    let recording = false;

    document.getElementById("startRecording").addEventListener("click", () => {
        fetch("/start_recording", { method: "POST" })
            .then(response => response.json())
            .then(data => {
                console.log(data);
                document.getElementById("recordingIndicator").classList.remove("hidden");
                document.getElementById("pauseRecording").classList.remove("hidden");
                document.getElementById("stopRecording").classList.remove("hidden");
                recording = true;
            });
    });

    document.getElementById("stopRecording").addEventListener("click", () => {
        fetch("/stop_recording", { method: "POST" })
            .then(response => response.json())
            .then(data => {
                document.getElementById("recordingIndicator").classList.add("hidden");
                console.log(data);

                if (data.file) {
                    transcribeAudio(data.file);
                }
            });
    });

    function transcribeAudio(filePath) {
        fetch("/transcribe", {
            method: "POST",
            body: JSON.stringify({ file_path: filePath }),
            headers: { "Content-Type": "application/json" }
        })
            .then(response => response.json())
            .then(data => {
                document.getElementById("transcriptionPanel").classList.remove("hidden");
                document.getElementById("transcriptionText").textContent = data.transcription || data.error;
            });
    }

    document.getElementById("uploadFile").addEventListener("click", () => {
        let file = document.getElementById("audioFile").files[0];
        let formData = new FormData();
        formData.append("audio", file);

        fetch("/upload", { method: "POST", body: formData })
            .then(response => response.json())
            .then(data => {
                document.getElementById("uploadTranscriptionPanel").classList.remove("hidden");
                document.getElementById("uploadTranscriptionText").textContent = data.transcription || data.error;
            });
    });
});
