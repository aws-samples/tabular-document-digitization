import React from "react";
import { StoreProvider } from "easy-peasy";
import { ThemeProvider } from "styled-components";

import { store } from "appstore";
import Main from "components/main/Main";
import "bootstrap/dist/css/bootstrap.min.css";
import "./App.css";
import { theme } from "styles/theme";
import { InputProvider } from "sagemaker-worker";

function App() {
  return (
    <InputProvider>
      <StoreProvider store={store}>
        <ThemeProvider theme={theme}>
          <Main />
        </ThemeProvider>
      </StoreProvider>
    </InputProvider>
  );
}

export default App;
