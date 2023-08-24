import React from "react";
import withStyles from "@material-ui/core/styles/withStyles";
import { DEFAULT_STATUS } from "./config";

const useStyles = () => ({
  messageBox: {
    margin: "10px 0 20px 0",
  },
});

const StatusMessage = ({ classes, statusMessage }) => {
  return (
    <div className={classes.messageBox}>
      <span>
        Status: {statusMessage === null ? DEFAULT_STATUS : statusMessage}
      </span>
    </div>
  );
};

export default withStyles(useStyles)(StatusMessage);
