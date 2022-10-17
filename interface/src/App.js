import React, { useState, useEffect, useRef } from "react";
import { Button } from "react-bootstrap";
import withStyles from "@material-ui/core/styles/withStyles";
import Typography from "@material-ui/core/Typography";
import 'bootstrap/dist/css/bootstrap.min.css';
import "./App.css";
import TranscribeOutput from "./TranscribeOutput";
import SettingsSections from "./SettingsSection";
import { ReactMic } from 'react-mic';
import axios from "axios";
import { PulseLoader } from "react-spinners";

const useStyles = () => ({
  root: {
    display: 'flex',
    flex: '1',
    margin: '100px 0px 100px 0px',
    alignItems: 'center',
    textAlign: 'center',
    flexDirection: 'column',
  },
  title: {
    marginBottom: '30px',
  },
  settingsSection: {
    marginBottom: '20px',
    display: 'flex',
    width: '100%',
  },
  buttonsSection: {
    marginBottom: '40px',
  },
  recordIllustration: {
    width: '100px',
  }
});

const App = ({ classes }) => {
  const [transcribedData, setTranscribedData] = useState([]);
  const [interimTranscribedData, ] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [isTranscribing, setIsTranscribing] = useState(false);
  const [selectedLanguage, setSelectedLanguage] = useState('english');
  const [selectedModel, setSelectedModel] = useState(1);
  const [transcribeTimeout, setTranscribeTimout] = useState(5);
  const [stopTranscriptionSession, setStopTranscriptionSession] = useState(false);  

  const intervalRef = useRef(null);
  
  const stopTranscriptionSessionRef = useRef(stopTranscriptionSession);
  stopTranscriptionSessionRef.current = stopTranscriptionSession;

  const selectedLangRef = useRef(selectedLanguage);
  selectedLangRef.current = selectedLanguage;

  const selectedModelRef = useRef(selectedModel);
  selectedModelRef.current = selectedModel;

  const supportedLanguages = ['english', 'chinese', 'german', 'spanish', 'russian', 'korean', 'french', 'japanese', 'portuguese', 'turkish', 'polish', 'catalan', 'dutch', 'arabic', 'swedish', 'italian', 'indonesian', 'hindi', 'finnish', 'vietnamese', 'hebrew', 'ukrainian', 'greek', 'malay', 'czech', 'romanian', 'danish', 'hungarian', 'tamil', 'norwegian', 'thai', 'urdu', 'croatian', 'bulgarian', 'lithuanian', 'latin', 'maori', 'malayalam', 'welsh', 'slovak', 'telugu', 'persian', 'latvian', 'bengali', 'serbian', 'azerbaijani', 'slovenian', 'kannada', 'estonian', 'macedonian', 'breton', 'basque', 'icelandic', 'armenian', 'nepali', 'mongolian', 'bosnian', 'kazakh', 'albanian', 'swahili', 'galician', 'marathi', 'punjabi', 'sinhala', 'khmer', 'shona', 'yoruba', 'somali', 'afrikaans', 'occitan', 'georgian', 'belarusian', 'tajik', 'sindhi', 'gujarati', 'amharic', 'yiddish', 'lao', 'uzbek', 'faroese', 'haitian creole', 'pashto', 'turkmen', 'nynorsk', 'maltese', 'sanskrit', 'luxembourgish', 'myanmar', 'tibetan', 'tagalog', 'malagasy', 'assamese', 'tatar', 'hawaiian', 'lingala', 'hausa', 'bashkir', 'javanese', 'sundanese']

  const modelOptions = ['tiny', 'base', 'small', 'medium', 'large']

  useEffect(() => {
    return () => clearInterval(intervalRef.current);
  }, []);


  function handleTranscribeTimeoutChange(newTimeout) {
    setTranscribeTimout(newTimeout)
  }

  function startRecording() {
    setStopTranscriptionSession(false)
    setIsRecording(true)
    intervalRef.current = setInterval(transcribeInterim, transcribeTimeout * 1000)
  }

  function stopRecording() {
    clearInterval(intervalRef.current);
    setStopTranscriptionSession(true)
    setIsRecording(false)
    setIsTranscribing(false)
  }

  function onData(recordedBlob) {
    // console.log('chunk of real-time data is: ', recordedBlob);
  }

  function onStop(recordedBlob) {
    transcribeRecording(recordedBlob)
    setIsTranscribing(true)  
  }

  function transcribeInterim() {
    clearInterval(intervalRef.current);
    setIsRecording(false)
  }

  function transcribeRecording(recordedBlob) {
    const headers = {
      "content-type": "multipart/form-data",
    };
    const formData = new FormData();
    formData.append("language", selectedLangRef.current)
    formData.append("model_size", modelOptions[selectedModelRef.current])
    formData.append("audio_data", recordedBlob.blob, 'temp_recording');
    axios.post("http://0.0.0.0:8000/transcribe", formData, { headers })
      .then((res) => {
        setTranscribedData(oldData => [...oldData, res.data])
        setIsTranscribing(false)
        intervalRef.current = setInterval(transcribeInterim, transcribeTimeout * 1000)
      });
      
      if (!stopTranscriptionSessionRef.current){
        setIsRecording(true)    
      }
  }

  return (
    <div className={classes.root}>
      <div className={classes.title}>
        <Typography variant="h3">
          Whisper Playground <span role="img" aria-label="microphone-emoji">🎤</span>
        </Typography>
      </div>
      <div className={classes.settingsSection}>
        <SettingsSections disabled={isTranscribing || isRecording} possibleLanguages={supportedLanguages} selectedLanguage={selectedLanguage}
          onLanguageChange={setSelectedLanguage} modelOptions={modelOptions} selectedModel={selectedModel} onModelChange={setSelectedModel}
          transcribeTimeout={transcribeTimeout} onTranscribeTiemoutChanged={handleTranscribeTimeoutChange} />
      </div>
      <div className={classes.buttonsSection} >
        {!isRecording && !isTranscribing && <Button onClick={startRecording} variant="primary">Start transcribing</Button>}
        {(isRecording || isTranscribing) && <Button onClick={stopRecording} variant="danger" disabled={stopTranscriptionSessionRef.current}>Stop</Button>}
      </div>

      <div className="recordIllustration">
        <ReactMic record={isRecording} className="sound-wave" onStop={onStop}
          onData={onData} strokeColor="#0d6efd" backgroundColor="#f6f6ef" />
      </div>

      <div>
        <TranscribeOutput transcribedText={transcribedData} interimTranscribedText={interimTranscribedData} />
        <PulseLoader sizeUnit={"px"} size={20} color="purple" loading={isTranscribing} />
      </div>
    </div>
  );
}

export default withStyles(useStyles)(App);
