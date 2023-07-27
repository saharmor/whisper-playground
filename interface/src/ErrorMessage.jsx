import React, { useEffect } from "react";
import withStyles from "@material-ui/core/styles/withStyles";

const useStyles = () => ({
  errorPopup: {
    backgroundColor: "#ff0000",
    color: "#ffffff",
    padding: "10px 20px",
    borderRadius: "10px",
    boxShadow: "0px 2px 4px rgba(0, 0, 0, 0.2)",
    marginBottom: "20px",
  },
});

const ErrorMessage = ({ classes, message, setErrorMessage }) => {
  useEffect(() => {
    const timer = setTimeout(() => {
      // Automatically clear the error message after 5 seconds
      setErrorMessage(null);
    }, 5000);

    return () => {
      clearTimeout(timer);
    };
  }, []);

  return (
    <div className={classes.errorPopup}>
      <span>{message}</span>
    </div>
  );
};

export default withStyles(useStyles)(ErrorMessage);
