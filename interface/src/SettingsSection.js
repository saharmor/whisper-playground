import React from "react";
import { Grid, FormControl, InputLabel } from "@material-ui/core";
import Select from '@material-ui/core/Select';
import MenuItem from '@material-ui/core/MenuItem';
import TextField from '@material-ui/core/TextField';
import Autocomplete from '@material-ui/lab/Autocomplete';


const SettingsSections = ({ disabled, possibleLanguages, selectedLanguage, onLanguageChange,
  modelOptions, selectedModel, onModelChange, transcribeTimeout, onTranscribeTiemoutChanged }) => {

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
        <FormControl variant="standard" style={{ minWidth: 120 }}>
          <Autocomplete id="language-select" disableClearable options={possibleLanguages} getOptionLabel={(option) => option}
            disabled={disabled} value={selectedLanguage} onChange={(event, newValue) => {
              onLanguageChange(newValue);
            }}
            renderInput={(params) => <TextField {...params} label="Language" />} />
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
