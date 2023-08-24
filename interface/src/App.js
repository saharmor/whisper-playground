import React, { useState, useRef } from "react";
import { Button } from "react-bootstrap";
import withStyles from "@material-ui/core/styles/withStyles";
import Typography from "@material-ui/core/Typography";
import "bootstrap/dist/css/bootstrap.min.css";
import "./App.css";
import TranscribeOutput from "./TranscribeOutput";
import SettingsSections from "./SettingsSection";
import ErrorMessage from "./ErrorMessage";
import Message from "./Message";
import {
  MIC_SAMPLE_RATE,
  BLOCK_SIZE,
  WHISPER_MODEL_OPTIONS,
  TRANSCRIPTION_METHODS,
  SUPPORTED_LANGUAGES,
  BACKEND_ADDRESS,
  STEP_SIZE,
  INITIALIZATION_DURATION,
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
  const [errorMessages, setErrorMessages] = useState(null);
  const [message, setMessage] = useState(null);
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

  const setErrorMessage = (errorMessage) => {
    setMessage(null);
    setErrorMessages([errorMessage]);
  };

  const stopOnError = (errorMessage) => {
    setErrorMessage(errorMessage);
    stopRecording();
    setIsRecording(false);
    setIsStreamPending(false);
    if (socketRef.current) {
      socketRef.current.disconnect();
    }
  };

  const setNewMessage = (newMessage) => {
    setMessage(null);
    setMessage(newMessage);
  };

  function handleTranscribedData(data) {
    if (!isStreamPending) setMessage(null);
    if (transcriptionMethod === "real-time") {
      setTranscribedData((prevData) => [...prevData, ...data]);
    } else if (transcriptionMethod === "sequential") {
      setTranscribedData(data);
    }
  }

  const validateConfig = () => {
    const errorMessages = [];
    if (beamSize < 1) {
      errorMessages.push("Beam size must be equal to or larger than 1");
    } else if (beamSize % 1 !== 0) {
      errorMessages.push("Beam size must be a whole number");
    }
    if (transcribeTimeout < STEP_SIZE) {
      errorMessages.push(
        `Transcription timeout must be equal or larger than ${STEP_SIZE}`
      );
    }
    let selectionFields = [
      selectedModel,
      selectedLanguage,
      transcriptionMethod,
    ];
    let emptySelectionFieldExists = selectionFields.some(
      (field) => field === null
    );
    if (emptySelectionFieldExists) {
      errorMessages.push("Selection fields must not be empty");
    }
    if (errorMessages.length > 0) {
      setMessage(null);
      setErrorMessages(errorMessages);
      return false;
    }
    return true;
  };

  const calculateDelay = () => {
    const batch_size = Math.floor(transcribeTimeout / STEP_SIZE);
    const delay = batch_size * STEP_SIZE - STEP_SIZE;
    return delay + INITIALIZATION_DURATION;
  };

  function startStream() {
    const isConfigValid = validateConfig();
    if (!isConfigValid) return;
    setIsStreamPending(true);
    navigator.mediaDevices
      .getUserMedia({ audio: true })
      .then(function (s) {
        streamRef.current = s;

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

          if (socketRef.current !== null && !isStreamPending) {
            socketRef.current.emit("audioChunk", b64encode(data));
          }
        };

        const config = {
          language: selectedLanguage,
          model: selectedModel,
          transcribeTimeout: transcribeTimeout,
          beamSize: beamSize,
          transcriptionMethod: transcriptionMethod,
        };

        socketRef.current = new io.connect(BACKEND_ADDRESS, {
          transports: ["websocket"],
          query: config,
        });

        setNewMessage("Connecting to server...");

        // When the WebSocket connection is open, start sending the audio data.
        socketRef.current.on("whisperingStarted", function () {
          if (transcriptionMethod === "real-time") {
            setNewMessage(
              `Transcription starts ${calculateDelay()} seconds after you start speaking.`
            );
          } else if (transcriptionMethod === "sequential") {
            setNewMessage(
              `Transcription starts ${transcribeTimeout} seconds after you start speaking.`
            );
          }
          setIsStreamPending(false);
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
    if (audioContextRef.current !== null) {
      audioContextRef.current.close();
    }
  }

  function stopStream() {
    setIsStreamPending(true);
    setNewMessage("Ending stream, transcribing remaining audio data...");
    socketRef.current.emit("stopWhispering");
    stopRecording();
    setAudioData([]);
    socketRef.current.on("whisperingStopped", function () {
      setIsStreamPending(false);
      setIsRecording(false);
      setNewMessage("Stream ended.");
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
      {errorMessages && (
        <ErrorMessage
          messages={errorMessages}
          setErrorMessages={setErrorMessages}
        />
      )}
      {message && <Message message={message} />}
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
