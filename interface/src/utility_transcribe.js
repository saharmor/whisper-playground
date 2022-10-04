import axios from "axios";


let gumStream = null;
let recorder = null;
let audioContext = null;


let RecorderObj = {
  startRecording: function () {
    console.log("Recording started here");
    let constraints = {
      audio: true,
      video: false
    }

    audioContext = new window.AudioContext();

    navigator.mediaDevices
      .getUserMedia(constraints)
      .then(function (stream) {
        gumStream = stream;
        let input = audioContext.createMediaStreamSource(stream);

        recorder = new window.Recorder(input, {
          numChannels: 1
        })

        recorder.record();
        console.log("Recording started");
      }).catch(function (err) {
        //enable the record button if getUserMedia() fails
        console.log("Recording failed", err);
      });
  },

  onStop: function (blob) {
    console.log("uploading...");

    let data = new FormData();

    data.append('text', "this is the transcription of the audio file");
    data.append('wavfile', blob, "recording.wav");

    const config = {
      headers: { 'content-type': 'multipart/form-data' }
    }
    axios.post('http://localhost:8000/transcribe/', data, config);
  },

  stopRecording: function () {
    console.log("stopButton clicked");

    recorder.stop(); //stop microphone access
    gumStream.getAudioTracks()[0].stop();

    recorder.exportWAV(RecorderObj.onStop);
  },

}
export default RecorderObj;
