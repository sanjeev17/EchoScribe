let recorder;
let audioChunks = [];

chrome.action.onClicked.addListener((tab) => {
    chrome.tabCapture.capture({ audio: true, video: false }, (stream) => {
        recorder = new MediaRecorder(stream);
        recorder.ondataavailable = (event) => audioChunks.push(event.data);
        recorder.onstop = () => {
            let blob = new Blob(audioChunks, { type: "audio/wav" });
            let url = URL.createObjectURL(blob);

            // Send recorded audio to Python server
            fetch("http://127.0.0.1:5000/upload", {
                method: "POST",
                body: blob
            }).then(response => response.text()).then(data => {
                console.log("Transcription: ", data);
            });

            audioChunks = [];
        };
        recorder.start();
        setTimeout(() => recorder.stop(), 15000); // Record for 15s
    });
});
