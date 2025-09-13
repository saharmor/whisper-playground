import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";
import App from "./App";

// Check if the environment is production
const isProduction = process.env.REACT_APP_NODE_ENV === 'PROD';

// Override console.log in production
if (isProduction) {
  console.log = function () {};
}

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
