import App from "./App";

import React, { useState } from "react";
import withStyles from "@material-ui/core/styles/withStyles";
import 'bootstrap/dist/css/bootstrap.min.css';
import "./App.css";
import _ from 'lodash';


const MainApp = ({ }) => {
    const [stopTranscriptionSession, setStopTranscriptionSession] = useState(false);

    return (
        <App stopTranscriptionSession={stopTranscriptionSession} setStopTranscriptionSession={setStopTranscriptionSession}/>
    )

}
export default MainApp;
