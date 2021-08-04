import React from "react";
import styled from "styled-components";
import { Document, Page } from "react-pdf";

const PdfSidebarContainer = styled.div`
  flex: 1 0 auto;
  padding: 1.5rem;
  overflow-y: scroll;
  overflow-x: hidden;
  max-width: 188px;
  background: ${(p) => p.theme.gray50};
`;

const PdfSidebarPageContainer = styled.div<{
  selected: boolean;
}>`
  flex: 1 0 auto;
  overflow: hidden;
  cursor: pointer;
  margin-bottom: 1rem;

  .react-pdf__Page {
    ${(p) => (p.selected ? `border: 3px solid ${p.theme.blue};` : "")}
    ${(p) => (!p.selected ? "margin: 3px;" : "")}
    box-shadow: 0px 1px 5px rgba(0, 0, 0, 0.3);
  }
`;

const PageNumber = styled.div`
  display: flex;
  justify-content: center;
  font-weight: 500;
  font-size: 80%;
  padding-top: 0.5rem;
`;

export default (props: {
  url: string;
  pageNumber: number;
  numPages: number;
  setSelectedPage: (page: number) => void;
}) => {
  const { url, pageNumber, numPages, setSelectedPage } = props;

  return (
    <PdfSidebarContainer>
      <Document file={url}>
        {Array.from(new Array(numPages), (el, index) => {
          return (
            <PdfSidebarPageContainer
              key={`page_${index + 1}`}
              color="coral"
              selected={index === pageNumber - 1}
            >
              <div
                onClick={() => {
                  setSelectedPage(index + 1);
                }}
              >
                <Page
                  pageNumber={index + 1}
                  scale={0.155}
                  renderTextLayer={false}
                  renderAnnotationLayer={false}
                />
                <PageNumber className="d-flex justify-content-center font-weight-">
                  {index + 1}
                </PageNumber>
              </div>
            </PdfSidebarPageContainer>
          );
        })}
      </Document>
    </PdfSidebarContainer>
  );
};
