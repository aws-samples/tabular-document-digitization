import React, { ReactElement, useEffect } from "react";
import styled from "styled-components";
import {
  RenderPageProps,
  Worker,
  Viewer,
  PageChangeEvent,
  SpecialZoomLevel,
} from "@react-pdf-viewer/core";
// Import the styles
import "@react-pdf-viewer/core/lib/styles/index.css";
import {
  defaultLayoutPlugin,
  ToolbarProps,
  ToolbarSlot,
} from "@react-pdf-viewer/default-layout";
// Import styles
import "@react-pdf-viewer/default-layout/lib/styles/index.css";
import { pageNavigationPlugin } from "@react-pdf-viewer/page-navigation";
// Import styles
import "@react-pdf-viewer/page-navigation/lib/styles/index.css";
import { useStoreActions, useStoreState } from "../../appstore";
import BoxAnnotationLayer from "./BoxAnnotationLayer";
import { darken } from "polished";

const renderPage = (props: RenderPageProps) => {
  return (
    <>
      {props.svgLayer.children}
      {props.textLayer.children}
      {props.annotationLayer.children}
      <BoxAnnotationLayer pageIndex={props.pageIndex} />
    </>
  );
};

const renderToolbar = (Toolbar: (props: ToolbarProps) => ReactElement) => (
  <Toolbar>
    {(slots: ToolbarSlot) => {
      const {
        CurrentPageInput,
        GoToNextPage,
        GoToPreviousPage,
        NumberOfPages,
        Zoom,
        ZoomIn,
        ZoomOut,
      } = slots;
      return (
        <div
          style={{
            alignItems: "center",
            display: "flex",
          }}
        >
          <div style={{ padding: "0px 2px" }}>
            <GoToPreviousPage />
          </div>
          <div style={{ padding: "0px 2px", display: "flex", alignItems: "center" }}>
            <CurrentPageInput /> &nbsp;/ <NumberOfPages />
          </div>
          <div style={{ padding: "0px 2px" }}>
            <GoToNextPage />
          </div>
          <div style={{ padding: "0px 2px", marginLeft: "auto" }}>
            <ZoomOut />
          </div>
          <div style={{ padding: "0px 2px" }}>
            <Zoom />
          </div>
          <div style={{ padding: "0px 2px" }}>
            <ZoomIn />
          </div>
        </div>
      );
    }}
  </Toolbar>
);

const ViewerContainer = styled.div`
  border-radius: 8px;
  height: 100%;
`;
const PDFComponentContainer = styled.div`
  width: 50%;
  overflow: auto;
  margin: 1rem 0.5rem;
  border-radius: 8px;
  box-shadow: 0 2.8px 2.2px rgba(0, 0, 0, 0.134),
    0 6.7px 5.3px rgba(0, 0, 0, 0.148);
  border: 4px solid ${(p) => darken(0.05, p.theme.gray200)};
`;

const PDFViewer = () => {
  //Store state
  const pdfUrl = useStoreState((s) => s.documentModel.url);
  const selectedPage = useStoreState(
    (s) => s.internal.selectedPageNumber
  );
  const newPageSetFromTable = useStoreState((s) => s.internal.newPageSetFromTable);
  const setNewPageFromTable = useStoreActions((s) => s.setNewPageFromTable);
  const setSelectedPage = useStoreActions((s) => s.setSelectedPageNumber);

  const defaultLayoutPluginInstance = defaultLayoutPlugin({ renderToolbar });

  const onPageChange = (e: PageChangeEvent) => {
    if (e.currentPage + 1 !== selectedPage && newPageSetFromTable===undefined) {
      setSelectedPage({pageNumber: e.currentPage + 1});
    }
    else if(newPageSetFromTable!==undefined) {
      setNewPageFromTable(undefined);
    }
  };
  const pageNavigationPluginInstance = pageNavigationPlugin();
  const { jumpToPage } = pageNavigationPluginInstance;

  useEffect(() => {
    if(newPageSetFromTable!==undefined) {
      jumpToPage(newPageSetFromTable-1);
    }
  }, [jumpToPage, newPageSetFromTable]);

  return (
    <PDFComponentContainer>
    <Worker workerUrl="https://unpkg.com/pdfjs-dist@2.6.347/build/pdf.worker.min.js">
      <ViewerContainer>
        {pdfUrl ? (
          <Viewer
            fileUrl={pdfUrl}
            defaultScale={SpecialZoomLevel.PageFit}
            renderPage={renderPage}
            plugins={[defaultLayoutPluginInstance, pageNavigationPluginInstance]}
            initialPage={selectedPage - 1}
            onPageChange={onPageChange}
          />
        ) : null}
      </ViewerContainer>
    </Worker>
    </PDFComponentContainer>
  );
};

export default PDFViewer;
