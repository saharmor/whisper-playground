import React, { useEffect, useRef } from "react";
import withStyles from "@material-ui/core/styles/withStyles";
import Typography from "@material-ui/core/Typography";

const useStyles = () => ({
  root: {
    maxWidth: "800px",
    display: "flex",
  },
  outputText: {
    marginLeft: "8px",
    color: "#ef395a",
  },
});

const TranscribeOutput = ({ data, classes }) => {
  const transcriptEndRef = useRef(null);

  const scrollToBottom = () => {
    transcriptEndRef.current.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [data]);

  function formatData(data) {
    let formattedText = "";
    let currentSpeaker = null;

    data.forEach((item) => {
      const speaker = item.speaker;
      const text = item.text;
      let speakerName = "";

      if (speaker === "unknown") {
        speakerName = "Unknown Speaker";
      } else {
        speakerName = `Speaker ${speaker + 1}`;
      }

      if (speaker !== currentSpeaker) {
        if (formattedText.length > 0) {
          formattedText += "\n\n";
        }
        formattedText += `${speakerName}: ${text}`;
        currentSpeaker = speaker;
      } else {
        formattedText += ` ${text}`;
      }
    });

    return formattedText;
  }

  // Format the transcription data
  const formattedTranscription = formatData(data);

  // Split the paragraphs by the new line character '\n'
  const paragraphs = formattedTranscription.split("\n");

  return (
    <div>
      {paragraphs.map((paragraph, index) => (
        <div key={index}>
          {index !== 0 && <br />}{" "}
          {/* Add two line breaks after the first paragraph */}
          <Typography variant="body1" component="p">
            {paragraph}
          </Typography>
        </div>
      ))}
      <div ref={transcriptEndRef}></div>
    </div>
  );
};

export default withStyles(useStyles)(TranscribeOutput);
