import React from "react";
import { Grid, FormControl, InputLabel } from "@material-ui/core";
import Select from "@material-ui/core/Select";
import MenuItem from "@material-ui/core/MenuItem";
import TextField from "@material-ui/core/TextField";
import Autocomplete from "@material-ui/lab/Autocomplete";

const SettingsSections = ({

  // MonsterAPI States Distructure Start
  transcriptionInterval,
  settranscriptionInterval,
  setLanguage,
  language,
  bestOf,
  removeSilence,
  setBestOf,
  setRemoveSilence,

  // MonsterAPI States Distructure End
  disabled,
  possibleLanguages,
  selectedLanguage,
  transcription,
  transcribeTimeout,
  beamSize,
  onLanguageChange,
  modelOptions,
  methodOptions,
  selectedModel,
  selectedMethod,
  onModelChange,
  onTranscribeTimeoutChange,
  onBeamSizeChange,
  onMethodChange
}) => {
  function onModelChangeLocal(event) {
    onModelChange(event.target.value);
  }

  function onTranscribeTimeoutChangedLocal(event) {
    onTranscribeTimeoutChange(event.target.value);
  }

  function onBeamSizeChangedLocal(event) {
    onBeamSizeChange(event.target.value);
  }

  function onMethodChangeLocal(event) {
    onMethodChange(event.target.value);
  }

  function onTranscriptionIntervalChangeLocal(event) {
    settranscriptionInterval(event.target.value);
  }

  function onBestofChangeLocal(event) {
    setBestOf(event.target.value);
  }

  function onRemoveSilenceChangeLocal(event) {
    setRemoveSilence(event.target.value);
  }

  function onLanguageChangeChangeLocal(newValue) {
    setLanguage(selectedLanguage.find(lang => lang.code === newValue.code));
  }
  

  return (
    <Grid
      container
      spacing={2}
      direction="row"
      justifyContent="center"
      alignItems="center"
    >
      {/* <Grid item>
        <FormControl variant="standard" sx={{ m: 2, minWidth: 220 }}>
          <InputLabel id="model-select-label">Model size</InputLabel>
          <Select
            labelId="model-select-label"
            value={selectedModel}
            onChange={(event) => onModelChangeLocal(event)}
            disabled={disabled}
          >
            {Object.keys(modelOptions).map((model) => {
              return (
                <MenuItem key={model} value={modelOptions[model]}>
                  {modelOptions[model]}
                </MenuItem>
              );
            })}
          </Select>
        </FormControl>
      </Grid> */}
      <Grid item>
        <FormControl variant="standard" style={{ minWidth: 120 }}>
          <Autocomplete
            id="language-select"
            disableClearable
            options={possibleLanguages}
            getOptionLabel={(option) => option.name}
            disabled={disabled}
            value={language}
            onChange={(event, newValue) => {
              onLanguageChangeChangeLocal(newValue);
            }}            
            renderInput={(params) => <TextField {...params} label="Language" />}
          />
        </FormControl>
      </Grid>
      <Grid item>
        <TextField
          label="Transcription Interval in Sec"
          type="number"
          value={transcriptionInterval}
          onChange={(event) => onTranscriptionIntervalChangeLocal(event)}
          disabled={disabled}
        />
      </Grid>
      <Grid item>
        <TextField
          label="bestOf"
          type="number"
          value={bestOf}
          onChange={(event) => onBestofChangeLocal(event)}
          disabled={disabled}
        />
      </Grid>
      <Grid item>
        <TextField
          label="Beam Size"
          type="number"
          value={beamSize}
          onChange={(event) => onBeamSizeChangedLocal(event)}
          disabled={disabled}
        />
      </Grid>

      <Grid item>
        <FormControl variant="standard" sx={{ m: 2, minWidth: 220 }}>
          <InputLabel id="model-select-label">Remove Silence</InputLabel>
          <Select
            labelId="model-select-label"
            value={removeSilence}
            onChange={(event) => onRemoveSilenceChangeLocal(event)}
            disabled={disabled}
          >
            <MenuItem key={"true"} value={"true"}>
              True
            </MenuItem>
            <MenuItem key={"false"} value={"false"}>
              False
            </MenuItem>
          </Select>
        </FormControl>
      </Grid>

      {/* <Grid item>
        <FormControl variant="standard" sx={{ m: 2, minWidth: 220 }}>
          <InputLabel id="model-select-label">Transcription Method</InputLabel>
          <Select
            labelId="model-select-label"
            value={selectedMethod}
            onChange={(event) => onMethodChangeLocal(event)}
            disabled={disabled}
          >
            {Object.keys(methodOptions).map((model) => {
              return (
                <MenuItem key={model} value={methodOptions[model]}>
                  {methodOptions[model]}
                </MenuItem>
              );
            })}
          </Select>
        </FormControl>
      </Grid> */}
    </Grid>
  );
};

export default SettingsSections;
