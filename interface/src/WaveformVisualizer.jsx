import React, { useRef, useEffect } from "react";

const WaveformVisualizer = ({ audioData }) => {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    const context = canvas.getContext("2d");

    const drawWaveform = () => {
      // Clear the canvas
      context.clearRect(0, 0, canvas.width, canvas.height);

      // Set up drawing parameters
      const width = canvas.width;
      const height = canvas.height;
      const step = Math.ceil(audioData.length / width);
      const amp = height / 2;

      // Start drawing the waveform
      context.beginPath();
      context.moveTo(0, amp);

      for (let i = 0; i < width; i++) {
        let min = 1.0;
        let max = -1.0;

        for (let j = 0; j < step; j++) {
          const dataIndex = i * step + j;
          if (dataIndex >= audioData.length) {
            break;
          }

          const datum = audioData[dataIndex];
          if (datum < min) {
            min = datum;
          }
          if (datum > max) {
            max = datum;
          }
        }

        const x = i;
        const y = (1 + min) * amp;
        const barHeight = Math.max(1, (max - min) * amp);

        // Draw a rectangle for each data point
        context.fillRect(x, y, 1, barHeight);
      }

      // Finish drawing the waveform
      context.lineTo(canvas.width, amp);
      context.stroke();
    };

    // Draw the waveform whenever the audio data changes
    drawWaveform();
  }, [audioData]);

  return <canvas ref={canvasRef} width={800} height={200}></canvas>;
};

export default WaveformVisualizer;
