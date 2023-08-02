import React from "react";
import { Grid, FormControl, InputLabel } from "@material-ui/core";
import Select from "@material-ui/core/Select";
import MenuItem from "@material-ui/core/MenuItem";
import TextField from "@material-ui/core/TextField";
import Autocomplete from "@material-ui/lab/Autocomplete";

const SettingsSections = ({
  disabled,
  possibleLanguages,
  selectedLanguage,
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

  return (
    <Grid
      container
      spacing={2}
      direction="row"
      justifyContent="center"
      alignItems="center"
    >
      <Grid item>
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
      </Grid>
      <Grid item>
        <FormControl variant="standard" style={{ minWidth: 120 }}>
          <Autocomplete
            id="language-select"
            disableClearable
            options={possibleLanguages}
            getOptionLabel={(option) => option}
            disabled={disabled}
            value={selectedLanguage}
            onChange={(event, newValue) => {
              onLanguageChange(newValue);
            }}
            renderInput={(params) => <TextField {...params} label="Language" />}
          />
        </FormControl>
      </Grid>
      <Grid item>
        <TextField
          label="Transcription Timeout"
          type="number"
          value={transcribeTimeout}
          onChange={(event) => onTranscribeTimeoutChangedLocal(event)}
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
      </Grid>
    </Grid>
  );
};

export default SettingsSections;
