import { createTypedHooks, createStore, Action, action } from "easy-peasy";
import { DocumentPage, ApplicationState, TableType, Metadata } from "./models";

export interface TabularHil {
  numPages: number;
  tableTypes: TableType[];
  pages: DocumentPage[];
  metadata?: Metadata;
}

interface InitAnnotationsPayload {
  pdfUrl: string;
  taskObject: TabularHil;
}

export interface ApplicationActions {
  // Initialize State
  initializeAnnotations: Action<ApplicationState, InitAnnotationsPayload>;

  // Annotation Actions
  updateTableCell: Action<
    ApplicationState,
    {
      pageNumber: number;
      table: number;
      row: number;
      column: number;
      value: string;
    }
  >;

  // Internal
  setSelectedPageNumber: Action<
    ApplicationState,
    {
      pageNumber: number;
    }
  >;
  setSelectedTableIndex: Action<
    ApplicationState,
    {
      tableIndex: number;
    }
  >;
  setSelectedTag: Action<ApplicationState, {tag: string | undefined;}>;
  setNumPages: Action<
    ApplicationState,
    {
      numPages: number;
    }
  >;
  setSelectedConfidenceScoreIndex: Action<
    ApplicationState,
    {
      selectedConfidenceScoreIndex: number | undefined;
    }
  >;
  setSelectedTableCell: Action<
    ApplicationState,
    {
      table: number;
      row: number;
      column: number;
    }
  >;
  setSelectedTableTableType: Action<ApplicationState, string | null>;
  setTableColumnType: Action<
    ApplicationState,
    {
      columnIndex: number;
      columnType: string | undefined;
    }
  >;
  setInitializeError: Action<ApplicationState, string>;
  setNewPageFromTable: Action<ApplicationState, number | undefined>;
}

export type ApplicationStateAndActions = ApplicationState & ApplicationActions;

// Initial (empty) application state
const applicationState: ApplicationState = {
  documentModel: {
    url: "",
    filename: "",
    numPages: 0,
    tableTypes: [],
    documentPages: [],
    metadata: undefined,
  },
  internal: {
    selectedPageNumber: 1,
    selectedTableIndex: 0,
    selectedTag: undefined,
    selectedConfidenceScoreIndex: undefined,
    selectedTableCell: undefined,
    initializeError: undefined,
    newPageSetFromTable: undefined
  },
};

const applicationActions: ApplicationActions = {
  // Initialize application state
  initializeAnnotations: action((state, payload) => {
    state.documentModel = {
      url: payload.pdfUrl,
      filename: payload.pdfUrl.split("/").pop()?.split("?")[0] || "",
      numPages: payload.taskObject.numPages,
      documentPages: payload.taskObject.pages,
      tableTypes: payload.taskObject.tableTypes,
      metadata: payload.taskObject.metadata
    };
  }),

  // Annotation Actions
  updateTableCell: action(
    (state, { pageNumber, table, row, column, value }) => {
      const page = state.documentModel.documentPages.find(
        (page) => page.pageNumber === pageNumber
      );
      if (!page) {
        return;
      }
      page.tables[table].rows[row][column].editedText = value;
    }
  ),

  // Internal
  setSelectedPageNumber: action((state, { pageNumber }) => {
    state.internal.selectedPageNumber = pageNumber;
    state.internal.selectedTableIndex = 0;
  }),
  setSelectedTableIndex: action((state, { tableIndex }) => {
    state.internal.selectedTableIndex = tableIndex;
  }),
  setSelectedTag: action((state, {tag}) => {
    state.internal.selectedTag = tag;
  }),
  setNumPages: action((state, { numPages }) => {
    state.documentModel.numPages = numPages;
  }),
  setSelectedConfidenceScoreIndex: action(
    (state, { selectedConfidenceScoreIndex }) => {
      state.internal.selectedConfidenceScoreIndex = selectedConfidenceScoreIndex;
    }
  ),
  setSelectedTableCell: action((state, { row, column }) => {
    state.internal.selectedTableCell = { row, column };
  }),
  setSelectedTableTableType: action((state, tableType) => {
    const documentPage = state.documentModel.documentPages.find(
      (page) => page.pageNumber === state.internal.selectedPageNumber
    );
    if (!documentPage) {
      return;
    }
    const selectedTable =
      documentPage.tables[state.internal.selectedTableIndex];
    // Set table type and clear any existing header column types
    selectedTable.tableType = tableType;
    selectedTable.headerColumnTypes = {};
  }),
  setTableColumnType: action((state, { columnIndex, columnType }) => {
    const documentPage = state.documentModel.documentPages.find(
      (page) => page.pageNumber === state.internal.selectedPageNumber
    );
    if (!documentPage) {
      return;
    }
    const selectedTable =
      documentPage.tables[state.internal.selectedTableIndex];

    if (!columnType && columnIndex in selectedTable.headerColumnTypes) {
      // Delete column type if user passed in columnType == undefined
      delete selectedTable.headerColumnTypes[columnIndex];
    } else if (columnType) {
      // Set column type
      selectedTable.headerColumnTypes[columnIndex] = columnType;
    }
  }),
  setInitializeError: action((state, message) => {
    state.internal.initializeError = message;
  }),
  setNewPageFromTable: action((state, pageIndex) => {
    state.internal.newPageSetFromTable = pageIndex;
  })
};

const applicationStateAndActions: ApplicationStateAndActions = {
  ...applicationState,

  ...applicationActions,
};

const store = createStore(applicationStateAndActions);

const {
  useStoreActions,
  useStoreState,
  useStoreDispatch,
  useStore,
} = createTypedHooks<ApplicationStateAndActions>();

export { useStoreActions, useStoreState, useStoreDispatch, useStore, store };
