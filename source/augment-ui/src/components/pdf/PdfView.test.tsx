import React from "react";
import PdfView from "./PdfView";
import { render } from "@testing-library/react";
import { ThemeProvider } from "styled-components";

import { theme } from "styles/theme";
import { pdfjs } from "react-pdf";

jest.mock("react-pdf", () => ({
  pdfjs: {
    GlobalWorkerOptions: {
      workerSrc: "",
    },
  },
  Page: () => <div>Page</div>,
  Document: () => <div>Document</div>,
}));

test("tests things", async () => {
  const filename = "test.pdf";
  const url = "https://example.com/test.pdf";
  const page = 0;
  const numPages = 5;
  const setNumPages = (page: number) => {};
  const setSelectedPage = (page: number) => {};
  const { container } = render(
    <ThemeProvider theme={theme}>
      <PdfView
        url={url}
        filename={filename}
        page={page}
        numPages={numPages}
        setNumPages={setNumPages}
        setSelectedPage={setSelectedPage}
      />
    </ThemeProvider>
  );
  expect(container.textContent).toContain(filename);
  expect(container.textContent).toContain(`Page ${page + 1} of ${numPages}`);
});
