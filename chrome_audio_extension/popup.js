document.getElementById("startRecording").addEventListener("click", async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const mediaRecorder = new MediaRecorder(stream);
    let audioChunks = [];

    mediaRecorder.ondataavailable = event => audioChunks.push(event.data);
    
    mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunks, { type: "audio/wav" });
        const formData = new FormData();
        formData.append("audio", audioBlob, "recorded_audio.wav");

        const response = await fetch("http://127.0.0.1:5000/upload", { method: "POST", body: formData });
        const data = await response.json();

        document.getElementById("status").textContent = data.transcription || "Error transcribing audio.";
    };

    mediaRecorder.start();
    setTimeout(() => mediaRecorder.stop(), 10000);
});
