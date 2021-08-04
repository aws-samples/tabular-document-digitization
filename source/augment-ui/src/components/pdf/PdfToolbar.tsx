import React from "react";
import styled from "styled-components";
import { darken } from "polished";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faPlusCircle } from "@fortawesome/free-solid-svg-icons/faPlusCircle";
import { faMinusCircle } from "@fortawesome/free-solid-svg-icons/faMinusCircle";
import { faArrowCircleRight } from "@fortawesome/free-solid-svg-icons/faArrowCircleRight";
import { faArrowCircleLeft } from "@fortawesome/free-solid-svg-icons/faArrowCircleLeft";
import { faSync } from "@fortawesome/free-solid-svg-icons/faSync";

const PdfToolbarContainer = styled.div`
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  background: ${(p) => p.theme.gray150};
  padding: 0.5rem;
  color: ${(p) => p.theme.gray400};
`;

const IconButton = styled.div<{
  disabled?: boolean;
}>`
  padding: 0.35rem 0.5rem;
  border-radius: 3px;
  ${(p) =>
    !p.disabled
      ? `
      &:hover {
        background: ${darken(0.05, p.theme.gray200)};
        cursor: pointer;
      }
    `
      : "pointer-events: none;"}
`;

const IconButtonDivider = styled.div`
  height: 1rem;
  margin: 0 0.5rem;
  border-left: 2px solid ${(p) => p.theme.gray400};
  display: block;
`;
const PdfTitleText = styled.div`
  font-size: 80%;
  font-weight: 700;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  padding: 0 0.5rem;
  max-width: 250px;
`;

const PdfToolbarText = styled.div`
  font-size: 80%;
  font-weight: 700;
  padding: 0 0.5rem;
  white-space: nowrap;
`;

export default (props: {
  zoomIn: () => void;
  zoomOut: () => void;
  resetTransform: () => void;
  filename: string;
  pageNumber: number;
  numPages: number;
  setSelectedPage: (pageNumber: number) => void;
}) => {
  const {
    zoomIn,
    zoomOut,
    resetTransform,
    filename,
    pageNumber,
    numPages,
    setSelectedPage,
  } = props;

  const handlePageChange = (next: boolean) => () => {
    const incr = next ? 1 : -1;
    setSelectedPage(pageNumber + incr);
  };

  const canClickNext = pageNumber < numPages - 1;
  const canClickPrev = pageNumber > 0;

  return (
    <PdfToolbarContainer>
      <PdfTitleText title={filename}>{filename}</PdfTitleText>
      <div className="d-flex align-items-center ">
        <IconButton title="Zoom out" onClick={zoomOut}>
          <FontAwesomeIcon icon={faMinusCircle} />
        </IconButton>
        <IconButton title="Zoom In" onClick={zoomIn}>
          <FontAwesomeIcon icon={faPlusCircle} />
        </IconButton>
        <IconButton title="Reset Zoom" onClick={resetTransform}>
          <FontAwesomeIcon icon={faSync} />
        </IconButton>
        <IconButtonDivider />
        <IconButton
          title="Previous Page"
          onClick={handlePageChange(false)}
          disabled={!canClickPrev}
        >
          <FontAwesomeIcon icon={faArrowCircleLeft} />
        </IconButton>
        <IconButton
          title="Next Page"
          onClick={handlePageChange(true)}
          disabled={!canClickNext}
        >
          <FontAwesomeIcon icon={faArrowCircleRight} />
        </IconButton>
        <IconButtonDivider />
        <PdfToolbarText>
          Page {pageNumber} of {numPages}
        </PdfToolbarText>
      </div>
    </PdfToolbarContainer>
  );
};
