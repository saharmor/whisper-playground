import React, { useState, useRef, useEffect } from "react";
import { Button } from "react-bootstrap";
import withStyles from "@material-ui/core/styles/withStyles";
import Typography from "@material-ui/core/Typography";
import "bootstrap/dist/css/bootstrap.min.css";
import "./App.css";
import TranscribeOutput from "./TranscribeOutput";
import SettingsSections from "./SettingsSection";
import ErrorMessage from "./ErrorMessage";
import StatusMessage from "./StatusMessage";
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
import MonsterApiClient from "monsterapi";
import { Grid, TextField } from "@material-ui/core";

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
  // Monsterapi utilization start
  const [monsterAPIToken, setMonsterAPIToken] = useState("");

  // Initialize MonsterAPI client
  const client = new MonsterApiClient(monsterAPIToken);
  const languages = [
    { code: "none", name: "None" },
    { code: "en", name: "English" },
    { code: "af", name: "Afrikaans" },
    { code: "am", name: "Amharic" },
    // Add the rest of the languages as objects with 'code' and 'name' properties
    { code: "ar", name: "Arabic" },
    { code: "zh", name: "Chinese" },
    // Add all the other languages here following the same structure
  ];

  const [transcriptionInterval, settranscriptionInterval] = useState(2);
  const [text, setText] = useState("");
  const [transcriptionFormat, setTranscriptionFormat] = useState("text");
  const [bestOf, setBestOf] = useState(8);
  const [numSpeakers, setNumSpeakers] = useState(2);
  const [diarize, setDiarize] = useState("false");
  const [removeSilence, setRemoveSilence] = useState("false");
  const [language, setLanguage] = useState();
  const [isLiveTranscribing, setIsLiveTranscribing] = useState(false);
  const mediaRecorderRef = useRef(null);
  const recordingIntervalRef = useRef(null);
  const [isProcessing, setIsProcessing] = useState(false);

  const processAudioBlob = async (blob) => {
    setIsProcessing(true);
    const file = new File([blob], "recorded_audio.wav", { type: blob.type });
    try {
      const uploadResponse = await client.uploadFile(file);
      const transcriptionResponse = await client.generate("whisper", {
        transcription_format: transcriptionFormat,
        beam_size: beamSize,
        best_of: bestOf,
        num_speakers: numSpeakers,
        diarize: diarize,
        remove_silence: removeSilence,
        language: language?.code || "en",
        file: uploadResponse,
      });
      setText((prevText) => prevText + " " + transcriptionResponse?.text);
    } catch (error) {
      console.error("Error during upload or transcription:", error);
    }
    setIsProcessing(false);
  };

  const startRecordingSegment = () => {
    navigator.mediaDevices
      .getUserMedia({ audio: true })
      .then((stream) => {
        // Set up MediaRecorder
        const mediaRecorder = new MediaRecorder(stream);
        mediaRecorderRef.current = mediaRecorder;
        const chunks = [];
        mediaRecorder.ondataavailable = (event) => {
          chunks.push(event.data);
        };
        mediaRecorder.onstop = () => {
          const blob = new Blob(chunks, { type: "audio/wav" });
          processAudioBlob(blob);
        };
        mediaRecorder.start();

        // Set up audio context for visualization
        const audioContext = new (window.AudioContext ||
          window.webkitAudioContext)();
        const source = audioContext.createMediaStreamSource(stream);
        const processor = audioContext.createScriptProcessor(4096, 1, 1);
        source.connect(processor);
        processor.connect(audioContext.destination);

        processor.onaudioprocess = (e) => {
          // This is where you capture audio for visualization
          const inputData = e.inputBuffer.getChannelData(0);
          const inputDataCopy = new Float32Array(inputData); // Copy the data
          setAudioData(inputDataCopy); // Update the state for visualization
        };

        // Stop recording after 5 seconds and process the audio
        setTimeout(() => {
          if (mediaRecorder.state !== "inactive") {
            mediaRecorder.stop();
            processor.disconnect(); // Stop processing audio data
            audioContext.close(); // Close the audio context
          }
        }, 5000);
      })
      .catch((error) => {
        console.error("Error accessing microphone:", error);
      });
  };

  const startLiveTranscription = () => {
    const isConfigValid = validateConfig();
    if (!isConfigValid) return;
    setIsLiveTranscribing(true);
    setIsRecording(true);
    setStatusMessage("Transcription in progress");
    startRecordingSegment(); // Start the first segment immediately
  };

  const stopLiveTranscription = () => {
    console.log("Stopping live transcription");
    setIsLiveTranscribing(false);
    setIsRecording(false);
    setStatusMessage("Ready to transcribe");
  
    if (mediaRecorderRef.current) {
      console.log("Media recorder reference exists");
      if (mediaRecorderRef.current.state === "recording") {
        console.log("Media recorder is recording. Stopping...");
        mediaRecorderRef.current.stop();
      } else {
        console.log("Media recorder is not recording.");
      }
    } else {
      console.log("Media recorder reference does not exist.");
    }
  
    clearInterval(recordingIntervalRef.current);
  };

  useEffect(() => {
    if (isLiveTranscribing && !isProcessing) {
      // Start a new recording segment after the previous has been processed
      recordingIntervalRef.current = setInterval(() => {
        startRecordingSegment();
      }, transcribeTimeout * 1000); // Slightly longer to account for processing
    }

    return () => {
      clearInterval(recordingIntervalRef.current);
    };
  }, [isLiveTranscribing, isProcessing]);

  // Monsterapi utilization end

  const [transcribedData, setTranscribedData] = useState([]);
  const [audioData, setAudioData] = useState([]);
  const [isRecording, setIsRecording] = useState(false);
  const [isStreamPending, setIsStreamPending] = useState(false);
  const [selectedLanguage, setSelectedLanguage] = useState("english");
  const [selectedModel, setSelectedModel] = useState("small");
  const [transcribeTimeout, setTranscribeTimeout] = useState(5);
  const [beamSize, setBeamSize] = useState(1);
  const [errorMessages, setErrorMessages] = useState(null);
  const [statusMessage, setStatusMessage] = useState(null);
  const [transcriptionMethod, setTranscriptionMethod] = useState("real-time");

  // const socketRef = useRef(null);

  // const audioContextRef = useRef(null);

  // const streamRef = useRef(null);

  // const isStreamEndingRef = useRef(false);

  // function b64encode(chunk) {
  //   // Convert the chunk array to a Float32Array
  //   const bytes = new Float32Array(chunk).buffer;

  //   // Encode the bytes as a base64 string
  //   let encoded = btoa(String.fromCharCode.apply(null, new Uint8Array(bytes)));

  //   // Return the encoded string as a UTF-8 encoded string
  //   return decodeURIComponent(encoded);
  // }

  // const setErrorMessage = (errorMessage) => {
  //   setStatusMessage(null);
  //   setErrorMessages([errorMessage]);
  // };

  // const stopOnError = (errorMessage) => {
  //   setErrorMessage(errorMessage);
  //   stopRecording();
  //   setIsRecording(false);
  //   setIsStreamPending(false);
  //   if (socketRef.current) {
  //     socketRef.current.disconnect();
  //   }
  // };

  // function handleTranscribedData(data) {
  //   if (!isStreamEndingRef.current) setStatusMessage("Transcribing...");
  //   if (transcriptionMethod === "real-time") {
  //     setTranscribedData((prevData) => [...prevData, ...data]);
  //   } else if (transcriptionMethod === "sequential") {
  //     setTranscribedData(data);
  //   }
  // }

  const validateConfig = () => {
    const errorMessages = [];

    if (!monsterAPIToken) {
      errorMessages.push(`MonsterAPI Token is required.`);
    }

    if (beamSize < 1) {
      errorMessages.push("Beam size must be equal to or larger than 1");
    } else if (beamSize % 1 !== 0) {
      errorMessages.push("Beam size must be a whole number");
    }
    if (transcriptionInterval < 0) {
      errorMessages.push(`Transcription Interval in Sec larger than ${0}`);
    }
    if (bestOf < 0) {
      errorMessages.push(`Best of must larger than ${0}`);
    }
    if (transcriptionInterval < 0) {
      errorMessages.push(`Transcription Interval in Sec larger than ${0}`);
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
      setStatusMessage(null);
      setErrorMessages(errorMessages);
      return false;
    }
    return true;
  };

  // const calculateDelay = () => {
  //   const batch_size = Math.floor(transcribeTimeout / STEP_SIZE);
  //   const delay = batch_size * STEP_SIZE - STEP_SIZE;
  //   return delay + INITIALIZATION_DURATION;
  // };

  // function startStream() {
  //   const isConfigValid = validateConfig();
  //   if (!isConfigValid) return;
  //   setIsStreamPending(true);
  //   navigator.mediaDevices
  //     .getUserMedia({ audio: true })
  //     .then(function (s) {
  //       streamRef.current = s;

  //       setIsRecording(true);
  //       audioContextRef.current = new (window.AudioContext ||
  //         window.webkitAudioContext)({
  //         sampleRate: MIC_SAMPLE_RATE,
  //       });
  //       var source = audioContextRef.current.createMediaStreamSource(
  //         streamRef.current
  //       );
  //       var processor = audioContextRef.current.createScriptProcessor(
  //         BLOCK_SIZE,
  //         1,
  //         1
  //       );
  //       source.connect(processor);
  //       processor.connect(audioContextRef.current.destination);

  //       processor.onaudioprocess = function (event) {
  //         var data = event.inputBuffer.getChannelData(0);
  //         setAudioData(new Float32Array(data));

  //         if (socketRef.current !== null && !isStreamPending) {
  //           socketRef.current.emit("audioChunk", b64encode(data));
  //         }
  //       };

  //       const config = {
  //         language: selectedLanguage,
  //         model: selectedModel,
  //         transcribeTimeout: transcribeTimeout,
  //         beamSize: beamSize,
  //         transcriptionMethod: transcriptionMethod,
  //       };

  //       socketRef.current = new io.connect(BACKEND_ADDRESS, {
  //         transports: ["websocket"],
  //         query: config,
  //       });

  //       setStatusMessage("Connecting to server...");

  //       // When the WebSocket connection is open, start sending the audio data.
  //       socketRef.current.on("whisperingStarted", function () {
  //         if (transcriptionMethod === "real-time") {
  //           setStatusMessage(
  //             `Transcription starts ${calculateDelay()} seconds after you start speaking.`
  //           );
  //         } else if (transcriptionMethod === "sequential") {
  //           setStatusMessage(
  //             `Transcription starts ${transcribeTimeout} seconds after you start speaking.`
  //           );
  //         }
  //         setIsStreamPending(false);
  //       });

  //       socketRef.current.on("noMoreClientsAllowed", () => {
  //         stopOnError("No more clients allowed, try again later");
  //       });

  //       socketRef.current.on(
  //         "transcriptionDataAvailable",
  //         (transcriptionData) => {
  //           console.log(`transcriptionData: ${transcriptionData}`);
  //           handleTranscribedData(transcriptionData);
  //         }
  //       );
  //     })
  //     .catch(function (error) {
  //       console.error("Error getting microphone input:", error);
  //       setErrorMessage("Microphone not working");
  //       setIsStreamPending(false);
  //       setIsRecording(false);
  //     });
  // }

  // function stopRecording() {
  //   streamRef.current.getTracks().forEach((track) => track.stop());
  //   if (audioContextRef.current !== null) {
  //     audioContextRef.current.close();
  //   }
  // }

  // function stopStream() {
  //   setIsStreamPending(true);
  //   setStatusMessage("Ending stream, transcribing remaining audio data...");
  //   isStreamEndingRef.current = true;
  //   socketRef.current.emit("stopWhispering");
  //   stopRecording();
  //   setAudioData([]);
  //   socketRef.current.on("whisperingStopped", function () {
  //     setIsStreamPending(false);
  //     setIsRecording(false);
  //     setStatusMessage("Stream ended.");
  //     socketRef.current.disconnect();
  //   });
  // }

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
          // Monster API States Start
          possibleLanguages={languages}
          language={language}
          selectedLanguage={languages}
          setLanguage={setLanguage}
          transcriptionInterval={transcriptionInterval}
          settranscriptionInterval={settranscriptionInterval}
          numSpeakers={numSpeakers}
          onLanguageChange={setLanguage}
          bestOf={bestOf}
          setBestOf={setBestOf}
          setNumSpeakers={setNumSpeakers}
          removeSilence={removeSilence}
          setRemoveSilence={setRemoveSilence}
          // Monster API States End
          disabled={isRecording}
          transcribeTimeout={transcribeTimeout}
          beamSize={beamSize}
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

      <Grid
        container
        spacing={2}
        direction="row"
        justifyContent="center"
        alignItems="center"
      >
        <Grid item 
        style={{ marginBottom: "2rem" }}
        >
          <TextField
            label="Enter MonsterAPI Token"
            type="text"
            value={monsterAPIToken}
            
            onChange={(event) => setMonsterAPIToken(event.target.value)}
          />
        </Grid>
        <Grid item>
          <a
            href="https://monsterapi.ai/signup"
            target="_blank"
            rel="noopener noreferrer"
          >
            Click here to get it
          </a>
        </Grid>
      </Grid>

      {errorMessages && (
        <ErrorMessage
          messages={errorMessages}
          setErrorMessages={setErrorMessages}
        />
      )}
      <StatusMessage statusMessage={statusMessage} />
      <div className={classes.buttonsSection}>
        {!isRecording && (
          <Button
            // onClick={startStream}
            // disabled={isStreamPending}
            onClick={startLiveTranscription}
            disabled={isLiveTranscribing}
            variant="primary"
          >
            Start transcribing
          </Button>
        )}
        {isRecording && (
          <Button
            // onClick={stopStream}
            // disabled={isStreamPending}
            onClick={stopLiveTranscription}
            disabled={!isLiveTranscribing}
            variant="danger"
          >
            Stop
          </Button>
        )}
      </div>
      <div>
        <WaveformVisualizer audioData={audioData} />
      </div>

      <div 
      // className={classes.transcribeOutput}
      // style={{maxHeight: "1000px !important", overflow: "auto"}}
      >
        
        {/* <TranscribeOutput data={transcribedData} /> */}
        <p style={{ whiteSpace: "pre-wrap"}}
        >{text}</p>
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
