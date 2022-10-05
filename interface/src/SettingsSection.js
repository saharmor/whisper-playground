import React from "react";
import Select from '@material-ui/core/Select';
import MenuItem from '@material-ui/core/MenuItem';
import TextField from '@material-ui/core/TextField';
import {
  Grid, FormControl,
  InputLabel
} from "@material-ui/core";

const SettingsSections = ({ disabled, possibleLanguages, selectedLanguage, onLanguageChange,
  modelOptions, selectedModel, onModelChange, transcribeTimeout, onTranscribeTiemoutChanged }) => {

  function onLangChangedLocal(event) {
    onLanguageChange(event.target.value)
  }

  function onModelChangeLocal(event) {
    onModelChange(event.target.value)
  }

  function onTranscribeTiemoutChangedLocal(event) {
    onTranscribeTiemoutChanged(event.target.value)
  }

  return (
    <Grid container spacing={2} direction="row" justifyContent="center" alignItems="center">
      <Grid item>
        <FormControl variant="standard" sx={{ m: 2, minWidth: 220 }}>
          <InputLabel id="model-select-label">Model size</InputLabel>
          <Select labelId="model-select-label" value={selectedModel} onChange={onModelChangeLocal} disabled={disabled}>
            {Object.keys(modelOptions).map((model) => {
              return <MenuItem key={model} value={model}>{modelOptions[model]}</MenuItem>
            })}
          </Select>
        </FormControl>
      </Grid>
      <Grid item>
        <FormControl variant="standard" sx={{ m: 1, minWidth: 220 }}>
          <InputLabel id="language-select-label">Language</InputLabel>
          <Select labelId="language-select-label" value={selectedLanguage} onChange={onLangChangedLocal} disabled={disabled}>
            {Object.keys(possibleLanguages).map((language) => {
              return <MenuItem key={language} value={language}>{possibleLanguages[language]}</MenuItem>
            })}
          </Select>
        </FormControl>
      </Grid>
      <Grid item xs={1}>
        <TextField id="transcribe-timeout" label="Transcribe timeout" value={transcribeTimeout}
          onChange={onTranscribeTiemoutChangedLocal} fullWidth disabled={disabled} />
      </Grid>
    </Grid>
  )
}

export default SettingsSections;
