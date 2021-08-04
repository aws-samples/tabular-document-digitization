export interface Metadata {
  sourceDocumentUrl?: string;
  rejected?: boolean;
  rejectedReason?: string;
}

export interface DocumentModel {
  url: string;
  filename: string;
  numPages: number;
  tableTypes: TableType[];
  documentPages: DocumentPage[];
  metadata?: Metadata;
}

export interface TableType {
  name: string;
  columnTypes?: string[];
}

export interface DocumentPage {
  pageNumber: number;
  tables: PageTable[];
}

export interface PageTable {
  tableType: string | null;
  headerColumnTypes: {
    [columnIndex: string]: string;
  };
  rows: TableCell[][];
}

export interface TableCell {
  text: string;
  editedText?: string;
  confidence: number;
  tag: string;
  boundingBox?: {
    top: number;
    left: number;
    width: number;
    height: number;
  }
}

export interface InternalState {
  selectedPageNumber: number;
  selectedTableIndex: number;
  selectedTag: string | undefined;
  selectedConfidenceScoreIndex: number | undefined;
  selectedTableCell:
    | {
        row: number;
        column: number;
      }
    | undefined;
  initializeError: string | undefined;
  newPageSetFromTable: number | undefined;
}

export interface ApplicationState {
  documentModel: DocumentModel;
  internal: InternalState;
}
