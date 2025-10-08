import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
// import { GoogleOAuthProvider } from '@react-oauth/google'; // Temporarily disabled
import App from "./App";
import "./index.css";

// const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID; // Temporarily disabled

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>
);
