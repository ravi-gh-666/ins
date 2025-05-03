import React from "react";
import ReactDOM from "react-dom/client";
import ScoreCard from "./App";
import CssBaseline from "@mui/material/CssBaseline";
import { ThemeProvider, createTheme } from "@mui/material/styles";

const theme = createTheme({
  palette: {
    primary: {
      main: "#d50060"
    },
    background: {
      default: "#f8fafc"
    }
  }
});

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <ScoreCard />
    </ThemeProvider>
  </React.StrictMode>
);