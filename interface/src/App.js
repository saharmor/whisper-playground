import React, { useState, useRef } from "react";
import { Button } from "react-bootstrap";
import withStyles from "@material-ui/core/styles/withStyles";
import Typography from "@material-ui/core/Typography";
import "bootstrap/dist/css/bootstrap.min.css";
import "./App.css";
import TranscribeOutput from "./TranscribeOutput";
import SettingsSections from "./SettingsSection";
import ErrorMessage from "./ErrorMessage";
import {
  MIC_SAMPLE_RATE,
  BLOCK_SIZE,
  WHISPER_MODEL_OPTIONS,
  TRANSCRIPTION_METHODS,
  SUPPORTED_LANGUAGES,
} from "./config";
import WaveformVisualizer from "./WaveformVisualizer";
import io from "socket.io-client";
import { PulseLoader } from "react-spinners";

const useStyles = () => ({
  root: {
    display: "flex",
    flex: "1",
    margin: "100px 0px 100px 0px",
    alignItems: "center",
    textAlign: "center",
    flexDirection: "column",
    padding: "30px",
  },
  title: {
    marginBottom: "30px",
  },
  settingsSection: {
    marginBottom: "20px",
    display: "flex",
    width: "100%",
  },
  transcribeOutput: {
    overflow: "auto",
    marginBottom: "40px",
    maxWidth: "1200px",
  },
  buttonsSection: {
    marginBottom: "40px",
  },
  recordIllustration: {
    width: "100px",
  },
});

const App = ({ classes }) => {
  const [transcribedData, setTranscribedData] = useState([]);
  const [audioData, setAudioData] = useState([]);
  const [isRecording, setIsRecording] = useState(false);
  const [isStreamPending, setIsStreamPending] = useState(false);
  const [selectedLanguage, setSelectedLanguage] = useState("english");
  const [selectedModel, setSelectedModel] = useState("small");
  const [transcribeTimeout, setTranscribeTimeout] = useState(5);
  const [beamSize, setBeamSize] = useState(1);
  const [errorMessage, setErrorMessage] = useState(null);
  const [transcriptionMethod, setTranscriptionMethod] = useState("real-time");

  const socketRef = useRef(null);

  const audioContextRef = useRef(null);

  const streamRef = useRef(null);

  function b64encode(chunk) {
    // Convert the chunk array to a Float32Array
    const bytes = new Float32Array(chunk).buffer;

    // Encode the bytes as a base64 string
    let encoded = btoa(String.fromCharCode.apply(null, new Uint8Array(bytes)));

    // Return the encoded string as a UTF-8 encoded string
    return decodeURIComponent(encoded);
  }

  const stopOnError = (errorMessage) => {
    setErrorMessage(errorMessage);
    stopRecording();
    setIsRecording(false);
    setIsStreamPending(false);
    if (socketRef.current) {
      socketRef.current.disconnect();
    }
  };

  function handleTranscribedData(data) {
    if (transcriptionMethod === "real-time") {
      setTranscribedData((prevData) => [...prevData, ...data]);
    } else if (transcriptionMethod === "sequential") {
      setTranscribedData(data);
    }
  }

  function startStream() {
    setIsStreamPending(true);
    navigator.mediaDevices
      .getUserMedia({ audio: true })
      .then(function (s) {
        streamRef.current = s;

        setIsRecording(true);

        const config = {
          language: selectedLanguage,
          model: selectedModel,
          transcribeTimeout: transcribeTimeout,
          beamSize: beamSize,
          transcriptionMethod: transcriptionMethod,
        };

        // Create a new WebSocket connection.
        socketRef.current = new io.connect("http://0.0.0.0:8000", {
          transports: ["websocket"],
          query: config,
        });

        // When the WebSocket connection is open, start sending the audio data.
        socketRef.current.on("whisperingStarted", function () {
          setIsStreamPending(false);
          setIsRecording(true);
          audioContextRef.current = new (window.AudioContext ||
            window.webkitAudioContext)({
            sampleRate: MIC_SAMPLE_RATE,
          });
          var source = audioContextRef.current.createMediaStreamSource(
            streamRef.current
          );
          var processor = audioContextRef.current.createScriptProcessor(
            BLOCK_SIZE,
            1,
            1
          );
          source.connect(processor);
          processor.connect(audioContextRef.current.destination);

          processor.onaudioprocess = function (event) {
            var data = event.inputBuffer.getChannelData(0);
            setAudioData(new Float32Array(data));

            socketRef.current.emit("audioChunk", b64encode(data));
          };
        });

        socketRef.current.on("clientAlreadyStreaming", () => {
          stopOnError(
            "You are already streaming, wait for the current stream to end"
          );
        });

        socketRef.current.on("noMoreClientsAllowed", () => {
          stopOnError("No more clients allowed, try again later");
        });

        socketRef.current.on(
          "transcriptionDataAvailable",
          (transcriptionData) => {
            console.log(`transcriptionData: ${transcriptionData}`);
            handleTranscribedData(transcriptionData);
          }
        );
      })
      .catch(function (error) {
        console.error("Error getting microphone input:", error);
        setErrorMessage("Microphone not working");
        setIsStreamPending(false);
        setIsRecording(false);
      });
  }

  function stopRecording() {
    streamRef.current.getTracks().forEach((track) => track.stop());
    audioContextRef.current.close();
  }

  function stopStream() {
    setIsStreamPending(true);
    socketRef.current.emit("stopWhispering");
    stopRecording();
    setAudioData([]);
    socketRef.current.on("whisperingStopped", function () {
      setIsStreamPending(false);
      setIsRecording(false);
      socketRef.current.disconnect();
    });
  }

  return (
    <div className={classes.root}>
      <div className={classes.title}>
        <Typography variant="h3">
          Whisper Playground{" "}
          <span role="img" aria-label="microphone-emoji">
            🎤
          </span>
        </Typography>
      </div>
      <div className={classes.settingsSection}>
        <SettingsSections
          disabled={isRecording}
          possibleLanguages={SUPPORTED_LANGUAGES}
          selectedLanguage={selectedLanguage}
          transcribeTimeout={transcribeTimeout}
          beamSize={beamSize}
          onLanguageChange={setSelectedLanguage}
          modelOptions={WHISPER_MODEL_OPTIONS}
          methodOptions={TRANSCRIPTION_METHODS}
          selectedModel={selectedModel}
          selectedMethod={transcriptionMethod}
          onModelChange={setSelectedModel}
          onTranscribeTimeoutChange={setTranscribeTimeout}
          onBeamSizeChange={setBeamSize}
          onMethodChange={setTranscriptionMethod}
        />
      </div>
      {errorMessage && (
        <ErrorMessage
          message={errorMessage}
          setErrorMessage={setErrorMessage}
        />
      )}
      <div className={classes.buttonsSection}>
        {!isRecording && (
          <Button
            onClick={startStream}
            disabled={isStreamPending}
            variant="primary"
          >
            Start transcribing
          </Button>
        )}
        {isRecording && (
          <Button
            onClick={stopStream}
            variant="danger"
            disabled={isStreamPending}
          >
            Stop
          </Button>
        )}
      </div>
      <div>
        <WaveformVisualizer audioData={audioData} />
      </div>

      <div className={classes.transcribeOutput}>
        <TranscribeOutput data={transcribedData} />
      </div>

      <PulseLoader
        sizeUnit={"px"}
        size={20}
        color="purple"
        loading={isStreamPending}
        className={classes.loadingIcon}
      />
    </div>
  );
};

export default withStyles(useStyles)(App);
