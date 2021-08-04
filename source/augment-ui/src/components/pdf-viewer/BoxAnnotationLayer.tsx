import React from "react";
import styled from "styled-components";
import { useStoreState } from "../../appstore";
import {DocumentPage, TableCell} from "../../appstore/models";

const BoxAnnotationLayerContainer = styled.div`
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  width: 100%;
`;

interface BoundingBoxProps {
  top: number;
  bottom: number;
  left: number;
  right: number;
  isSelected: boolean;
}

const BoundingBox = styled.div<BoundingBoxProps>`
  position: absolute;
  top: ${(props) => props.top}%;
  bottom: ${(props) => props.bottom}%;
  left: ${(props) => props.left}%;
  right: ${(props) => props.right}%;
  background: ${(props) => props.isSelected?`rgba(0, 123, 255, 0.2)`:"none"};
`;

const BoxAnnotationLayer = (props: { pageIndex: number }) => {
  const selectedTag = useStoreState((s) => s.internal.selectedTag);
  const cells = useStoreState((s) => {
    const pages = [...s.documentModel.documentPages];
    let currentPage: DocumentPage = pages[0];
    for(let i=0;i<pages.length;i++) {
      if(pages[i].pageNumber===props.pageIndex + 1){
        currentPage = pages[i];
        break;
      }
    }

    let cells: TableCell[] = [];
    for(let i=0;i<currentPage.tables.length;i++) {
      for(let j=0;j<currentPage.tables[i].rows.length;j++){
        cells = [...cells, ...currentPage.tables[i].rows[j]];
      }
    }
    return cells;
  });

  return (
    <BoxAnnotationLayerContainer>
      {cells.map((cell, index) => (
          <BoundingBox
            key={`${props.pageIndex}-${index}-${cell.tag}`}
            top={cell.boundingBox?cell.boundingBox.top*100:0}
            bottom={cell.boundingBox?(100 - (cell.boundingBox.top*100 + cell.boundingBox.height*100)):100}
            left={cell.boundingBox?cell.boundingBox.left*100:0}
            right={cell.boundingBox?(100 - (cell.boundingBox.left*100 + cell.boundingBox.width*100)):100}
            isSelected={
              selectedTag === cell.tag
                ? true
                : false
            }
          />
        ))}
    </BoxAnnotationLayerContainer>
  );
};

export default BoxAnnotationLayer;
