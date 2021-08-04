import React from "react";
import styled from "styled-components";
import { pdfjs } from "react-pdf";
import { TransformWrapper } from "react-zoom-pan-pinch";
import { darken } from "polished";

import PdfMain from "./PdfMain";
import PdfToolbar from "./PdfToolbar";
import PdfSidebar from "./PdfSidebar";

pdfjs.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.js`;

const PdfContentContainer = styled.div`
  display: flex;
  flex-direction: column;
  max-height: 100%;
  overflow: hidden;
`;

const PdfContentInner = styled.div`
  display: flex;
  flex-direction: row;
  max-height: 100%;
  overflow: hidden;
`;

const PdfContent = (props: {
  url: string;
  filename: string;
  pageNumber: number;
  numPages: number;
  setNumPages: (page: number) => void;
  setSelectedPage: (page: number) => void;
}) => {
  return (
    <PdfContentContainer>
      <TransformWrapper
        options={{
          minScale: 0.7,
          limitToBounds: false,
        }}
        defaultScale={0.7}
      >
        {({
          zoomIn,
          zoomOut,
          resetTransform,
        }: {
          zoomIn: () => void;
          zoomOut: () => void;
          resetTransform: () => void;
        }) => (
          <>
            <PdfToolbar
              zoomIn={zoomIn}
              zoomOut={zoomOut}
              resetTransform={resetTransform}
              {...props}
            />
            <PdfContentInner>
              <PdfSidebar {...props} />
              <PdfMain {...props} />
            </PdfContentInner>
          </>
        )}
      </TransformWrapper>
    </PdfContentContainer>
  );
};

const PdfViewContainer = styled.div`
  width: 50%;
  overflow: auto;
  margin: 1rem 0.5rem;
  background: ${(p) => p.theme.gray50};

  background: white;
  border-radius: 8px;
  box-shadow: 0 2.8px 2.2px rgba(0, 0, 0, 0.134),
    0 6.7px 5.3px rgba(0, 0, 0, 0.148);
  border: 4px solid ${(p) => darken(0.05, p.theme.gray200)};
`;

export default (props: {
  url: string;
  filename: string;
  pageNumber: number;
  numPages: number;
  setNumPages: (page: number) => void;
  setSelectedPage: (page: number) => void;
}) => {
  return (
    <PdfViewContainer>
      <PdfContent {...props} />
    </PdfViewContainer>
  );
};
