import React from "react";
import styled from "styled-components";
import { Document, Page } from "react-pdf";
import { TransformComponent } from "react-zoom-pan-pinch";

const PdfPageRenderContainer = styled.div`
  display: flex;
  flex-direction: column;
`;

const PdfRenderContainer = styled.div`
  cursor: grab;
  flex: 1;
  display: flex;
  justify-content: center;

  canvas {
    width: 100% !important;
    height: auto !important;
  }

  background: ${(p) => p.theme.gray100};

  .react-pdf__Document {
    box-shadow: 0px 1px 5px rgba(0, 0, 0, 0.3);
  }
`;

export default (props: {
  url: string;
  filename: string;
  pageNumber: number;
  numPages: number;
  setNumPages: (page: number) => void;
  setSelectedPage: (page: number) => void;
}) => {
  const { url, pageNumber, setNumPages } = props;

  return (
    <PdfPageRenderContainer>
      <PdfRenderContainer>
        <TransformComponent>
          <Document file={url} onLoadSuccess={(e) => setNumPages(e.numPages)}>
            <Page
              pageNumber={pageNumber}
              renderTextLayer={false}
              renderAnnotationLayer={false}
            />
          </Document>
        </TransformComponent>
      </PdfRenderContainer>
    </PdfPageRenderContainer>
  );
};
