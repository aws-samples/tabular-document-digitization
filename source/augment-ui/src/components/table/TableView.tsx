import React, { useCallback, useEffect, useState, useMemo } from "react";
import ReactDOM from "react-dom";
import { ButtonGroup, Button, Form } from "react-bootstrap";
import styled from "styled-components";
import DataGrid, { Cell, editors } from "react-data-grid";
import { lighten } from "polished";
import { filter } from "lodash";

import { useStoreState, useStoreActions } from "appstore";
import Utils from "utils";

const HEADER_INCOMPLETE_VALUE = "<Identify Column>";

const confidenceHeatmapRange = Utils.getConfidenceScoreHeatmapRange();

const getHeatmapIndex = (confidence: number) => {
  const range = Utils.getConfidenceScoreHeatmapRange();
  for (var i = 0; i < range.length; i++) {
    const { score } = range[i];
    if (confidence < score) {
      return i;
    }
  }
  return range.length - 1;
};

const TableViewContainer = styled.div`
  width: 50%;
  overflow: auto;
  margin: 1rem 0.5rem;
  display: flex;
  align-items: center;
  flex-direction: column;

  padding: 1rem 1.25rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 0px 4.2px rgba(0, 0, 0, 0.2), 0 6.7px 6.3px rgba(0, 0, 0, 0.158);
`;

const TableHeaderContainer = styled.div`
  display: flex;
  flex-direction: column;
  width: 100%;
`;

const TableHeaderTitle = styled.div`
  font-size: 16px;
  font-weight: 500;
  margin-bottom: 0.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const TableHeaderSubtitle = styled.div`
  font-size: 14px;
  font-weight: 700;
  margin-bottom: 0.5rem;
  color: ${(p) => p.theme.gray600};
  display: flex;
  justify-content: space-between;
  align-items: center;
  select {
    min-width: 200px;
  }
`;

const ConfidenceFilterContainer = styled.div`
  display: flex;
  flex-direction: row;
  align-self: start;
  font-size: 14px;
  padding: 0.5rem 0;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  font-weight: 300;
  border-bottom: 1px solid ${(p) => p.theme.gray100};
  margin-bottom: 0.5rem;
  .btn-group {
    flex-wrap: wrap;
    .btn {
      flex: 0;
      white-space: nowrap;
      display: flex;
      font-size: 12px;
      align-items: center;
      border-left: 1px solid ${(p) => p.theme.gray150};
      &:first-child {
        border-left: none;
      }
    }
  }
`;

const Square = styled.div`
  display: inline-block;
  height: 16px;
  width: 16px;
  margin-left: 0.5rem;
  background: ${(p) => p.color};
  word-wrap: none;
`;

const TableHeader = () => {
  const selectedPageNumber = useStoreState(
    (s) => s.internal.selectedPageNumber
  );
  const selectedTableIndex = useStoreState(
    (s) => s.internal.selectedTableIndex
  );
  const documentPage = useStoreState((s) =>
    s.documentModel.documentPages.find(
      (documentPage) => documentPage.pageNumber === selectedPageNumber
    )
  );
  const selectedTable =
    documentPage && documentPage.tables.length > 0
      ? documentPage.tables[selectedTableIndex]
      : undefined;
  const tableTypes = useStoreState((s) => s.documentModel.tableTypes);
  const selectedTableType =
    selectedTable && selectedTable.tableType
      ? tableTypes.find((t) => t.name === selectedTable.tableType)
      : undefined;
  const selectedTableTypeColumnTypes = selectedTableType?.columnTypes;

  // Total number of columns
  const numColumns =
    selectedTable && selectedTable.rows.length > 0
      ? selectedTable.rows[0].length
      : 0;
  // Number of columns the user has assigned values to
  const numAssignedColumns = filter(
    Object.values(selectedTable?.headerColumnTypes || []),
    (o) => o
  ).length;

  const numPages = useStoreState((s) => s.documentModel.numPages);
  const documentPages = useStoreState((s) => s.documentModel.documentPages);
  const selectedConfidenceScoreIndex = useStoreState(
    (s) => s.internal.selectedConfidenceScoreIndex
  );
  const setSelectedConfidenceScoreIndex = useStoreActions(
    (s) => s.setSelectedConfidenceScoreIndex
  );
  const setSelectedPageNumber = useStoreActions((s) => s.setSelectedPageNumber);
  const setSelectedTableIndex = useStoreActions((s) => s.setSelectedTableIndex);
  const setSelectedTableTableType = useStoreActions(
    (s) => s.setSelectedTableTableType
  );
  const setNewPageFromTable = useStoreActions((s) => s.setNewPageFromTable);

  if (documentPages.length === 0) {
    return <div className="text-muted">Loading...</div>;
  }

  const onSelectConfidenceScore = (index: number) => {
    if (selectedConfidenceScoreIndex === index) {
      setSelectedConfidenceScoreIndex({
        selectedConfidenceScoreIndex: undefined,
      });
      return;
    }
    setSelectedConfidenceScoreIndex({
      selectedConfidenceScoreIndex: index,
    });
  };

  const prevPage = () => {
    setSelectedPageNumber({ pageNumber: selectedPageNumber - 1 });
    setNewPageFromTable(selectedPageNumber - 1);
  };
  const nextPage = () => {
    setSelectedPageNumber({ pageNumber: selectedPageNumber + 1 });
    setNewPageFromTable(selectedPageNumber + 1);
  };
  const prevTable = () => {
    setSelectedTableIndex({ tableIndex: selectedTableIndex - 1 });
  };
  const nextTable = () => {
    setSelectedTableIndex({ tableIndex: selectedTableIndex + 1 });
  };
  const selectTableType = (event: React.ChangeEvent<HTMLInputElement>) => {
    const value = event.target.value || null;
    setSelectedTableTableType(value);
  };

  return (
    <TableHeaderContainer>
      <TableHeaderTitle>
        <div>
          Annotating Page {selectedPageNumber} of {numPages}
        </div>
        <div>
          <Button
            size="sm"
            variant="primary"
            className="mr-1"
            onClick={prevPage}
            disabled={selectedPageNumber === 1}
          >
            Previous Page
          </Button>
          <Button
            size="sm"
            variant="primary"
            onClick={nextPage}
            disabled={selectedPageNumber === numPages}
          >
            Next Page
          </Button>
        </div>
      </TableHeaderTitle>
      <TableHeaderSubtitle>
        {documentPage && selectedTable ? (
          <>
            <div>
              Table {selectedTableIndex + 1} of {documentPage.tables.length}
            </div>
            <div>
              <Button
                size="sm"
                variant="light"
                className="mr-1"
                onClick={prevTable}
                disabled={selectedTableIndex === 0}
              >
                Previous Table
              </Button>
              <Button
                size="sm"
                variant="light"
                onClick={nextTable}
                disabled={selectedTableIndex + 1 === documentPage.tables.length}
              >
                Next Table
              </Button>
            </div>
          </>
        ) : (
          <div className="text-success">
            No tables found on page {selectedPageNumber}
          </div>
        )}
      </TableHeaderSubtitle>
      <TableHeaderSubtitle>
        {documentPage && selectedTable ? (
          <>
            <div>Identify Table Type</div>
            <div>
              <Form.Control
                as="select"
                size="sm"
                value={selectedTable.tableType || ""}
                onChange={selectTableType}
              >
                <option value="">{"<Select Table Type>"}</option>
                {tableTypes.map((tableType, tableTypeIndex) => (
                  <option key={tableTypeIndex} value={tableType.name}>
                    {tableType.name}
                  </option>
                ))}
              </Form.Control>
            </div>
          </>
        ) : null}
      </TableHeaderSubtitle>

      {selectedTableType && !selectedTableTypeColumnTypes ? (
        <TableHeaderSubtitle>
          <div className="text-success">
            No column selection necessary for table type{" "}
            {`"${selectedTableType.name}"`}
          </div>
        </TableHeaderSubtitle>
      ) : null}

      {selectedTableType &&
      selectedTableTypeColumnTypes &&
      numAssignedColumns < numColumns ? (
        <TableHeaderSubtitle>
          <div className="text-warning">
            Please select {numColumns - numAssignedColumns} column types for
            {`"${selectedTableType.name}"`} table
          </div>
        </TableHeaderSubtitle>
      ) : null}

      {selectedTableType &&
      selectedTableTypeColumnTypes &&
      numAssignedColumns === numColumns ? (
        <TableHeaderSubtitle>
          <div className="text-success">
            Assigned {numAssignedColumns} / {numColumns} column types for{" "}
            {`"${selectedTableType.name}"`} table
          </div>
        </TableHeaderSubtitle>
      ) : null}

      <ConfidenceFilterContainer>
        <div className="mr-3 d-flex align-items-center ">Confidence Score</div>
        <ButtonGroup>
          {confidenceHeatmapRange.map(({ score, color }, index) => (
            <Button
              key={index}
              value={index}
              size="sm"
              variant="light"
              active={index === selectedConfidenceScoreIndex}
              onClick={() => onSelectConfidenceScore(index)}
            >
              {index === 0 ? "<" : ">"} {score * 100}% <Square color={color} />
            </Button>
          ))}
        </ButtonGroup>
      </ConfidenceFilterContainer>
    </TableHeaderContainer>
  );
};

const TableGridContainer = styled.div`
  flex: 1;
  width: 100%;
  overflow: auto;
  .react-grid-Grid {
    border: 0px;
  }
  .custom-cell-content {
    padding: 4px;
  }

  .react-grid-Main {
    height: 100%;
  }

  .react-grid-Container {
    height: 100%;
  }

  .react-grid-Grid {
    min-height: 100% !important;
  }

  .react-grid-Canvas {
    height: 100% !important;
  }
  .react-grid-HeaderCell {
    background: ${(p) => lighten(0.1, p.theme.gray100)};
    border-right: 1px dotted ${(p) => p.theme.gray100};
  }
  .react-grid-Cell {
    padding: 0;
    padding-left: 0px;
    padding-right: 0px;
    line-height: 2;
    border-right: 0px;
    border-top: 1px solid ${(p) => p.theme.gray100};
  }
  .cell-container.active {
    .react-grid-Cell__value {
      border: 4px solid ${(p) => "#ffff76"};
    }
    .custom-cell-content {
      padding: 0;
    }
  }

  .cell-container.header-complete {
    .react-grid-Cell__value {
      border: 1px solid ${(p) => p.theme.gray300};
      background: ${(p) => p.theme.gray200};
    }
    .custom-cell-content {
    }
  }
  .cell-container.header-incomplete {
    .react-grid-Cell__value {
      border: 1px solid ${(p) => lighten(0.35, p.theme.yellow)};
      background: ${(p) => lighten(0.3, p.theme.yellow)};
    }
    .custom-cell-content {
    }
  }
  .cell-container.header-disabled {
    .react-grid-Cell__value {
      border: 1px solid ${(p) => p.theme.gray300};
      background: ${(p) => p.theme.gray300};
      color: ${(p) => p.theme.gray600};
      font-style: italic;
    }
    .custom-cell-content {
      cursor: not-allowed;
    }
  }
`;
interface CellValue {
  value: string | number;
  selected: boolean;
  confidence: number;
  isColumnSelector: boolean;
  columnTypes?: string[];
}
interface RowData {
  [columnName: string]: CellValue;
}

interface RowDataUpdate {
  [columnName: string]: string;
}

type OptionType =
  | string
  | {
      id: string;
      value: string;
      title: string;
      text?: string;
    };
type CustomEditorProps = {
  options?: OptionType[];
};

interface ExcelColumn {
  editable: boolean;
  name: any;
  key: string;
  width: number;
  resizeable: boolean;
  filterable: boolean;
}

interface EditorBaseProps {
  value: any;
  column: ExcelColumn;
  height: number;
  onBlur: () => void;
  onCommit: () => void;
  onCommitCancel: () => void;
  rowData: any;
  rowMetaData: any;
}

class CustomTextAndSelectEditor extends editors.EditorBase<
  CustomEditorProps,
  {}
> {
  getInputNode() {
    const inputNode = super.getInputNode();
    if (!inputNode) {
      return ReactDOM.findDOMNode(this);
    }
    return inputNode;
  }

  render() {
    const value = this.props.value as CellValue;
    if (value.isColumnSelector) {
      return this.renderSelectEditor();
    } else {
      return this.renderTextEditor();
    }
  }

  renderTextEditor() {
    return (
      <input
        type="text"
        onBlur={this.props.onBlur}
        className="form-control"
        defaultValue={this.props.value.value}
      />
    );
  }

  onChange() {}

  renderSelectEditor() {
    const value = this.props.value as CellValue;
    if (!value.columnTypes) {
      return (
        <select style={this.getStyle()} disabled={true}>
          <option value="">{HEADER_INCOMPLETE_VALUE}</option>
        </select>
      );
    }
    return (
      <select
        style={this.getStyle()}
        defaultValue={value.value}
        onBlur={this.props.onBlur}
        onChange={this.onChange}
      >
        <option value="">{HEADER_INCOMPLETE_VALUE}</option>
        {value.columnTypes.map((name, index) => (
          <option key={index} value={name}>
            {name}
          </option>
        ))}
      </select>
    );
  }
}

class CustomCell extends React.Component<{
  value: CellValue;
}> {
  render() {
    const { value } = this.props;
    if (!value) {
      return null;
    }
    const classNames = ["cell-container"];
    if (value.selected) {
      classNames.push("active");
    }

    if (value.isColumnSelector && value.value) {
      classNames.push("header-complete");
    }
    if (value.isColumnSelector && !value.columnTypes) {
      classNames.push("header-disabled");
    } else if (
      value.isColumnSelector &&
      value.value === HEADER_INCOMPLETE_VALUE
    ) {
      classNames.push("header-incomplete");
    }
    return (
      <div className={classNames.join(" ")}>
        <Cell {...this.props} />
      </div>
    );
  }
}

const TableGrid = () => {
  const [rowData, setRowData] = useState<RowData[]>([]);

  const selectedPageNumber = useStoreState(
    (s) => s.internal.selectedPageNumber
  );
  const selectedTableIndex = useStoreState(
    (s) => s.internal.selectedTableIndex
  );
  const tableTypes = useStoreState((s) => s.documentModel.tableTypes);
  const documentPages = useStoreState((s) => s.documentModel.documentPages);
  const selectedPage = documentPages.find(
    (documentPage) => documentPage.pageNumber === selectedPageNumber
  );
  const selectedTable =
    selectedPage && selectedPage.tables.length > 0
      ? selectedPage.tables[selectedTableIndex]
      : undefined;

  const selectedTableType =
    selectedTable && selectedTable.tableType
      ? tableTypes.find((t) => t.name === selectedTable.tableType)
      : undefined;
  const selectedTableTypeColumnTypes = selectedTableType?.columnTypes;
  const selectedConfidenceScoreIndex = useStoreState(
    (s) => s.internal.selectedConfidenceScoreIndex
  );
  const numColumns =
    selectedTable && selectedTable.rows.length > 0
      ? selectedTable.rows[0].length
      : 0;
  const updateTableCell = useStoreActions((s) => s.updateTableCell);
  const setTableColumnType = useStoreActions((s) => s.setTableColumnType);

  const setSelectedTag = useStoreActions((s) => s.setSelectedTag);

  const confidenceHeatmapRange = Utils.getConfidenceScoreHeatmapRange();

  // Translate HIL Input document table rows into react-data-grid rows
  useEffect(() => {
    if (!selectedTable) {
      return;
    }
    const localRows: RowData[] = [];
    // Add header row for selecting column type
    const localRow: RowData = {};
    Array.from({ length: numColumns }, (x, i) => i).forEach((columnIndex) => {
      const columnIndexStr = `${columnIndex}`;
      const value = selectedTable.headerColumnTypes[columnIndexStr]
        ? selectedTable.headerColumnTypes[columnIndexStr]
        : HEADER_INCOMPLETE_VALUE;

      localRow[columnIndexStr] = {
        value: value,
        selected: false,
        confidence: 100,
        isColumnSelector: true,
        columnTypes: selectedTableTypeColumnTypes,
      };
    });
    localRows.push(localRow);

    // Add all other rows
    selectedTable.rows.forEach((row, rowIndex) => {
      const localRow: RowData = {};
      row.forEach((cell, columnIndex) => {
        // The textract pipeline outputs empty cells with 0% confidence.
        // Change to 100% confidence to not overload the heatmap with red
        // for empty cells
        const confidence = cell.text === "" ? 100 : cell.confidence;
        const heatmapIndex = getHeatmapIndex(confidence / 100);
        localRow[`${columnIndex}`] = {
          value: cell.editedText !== undefined ? cell.editedText : cell.text,
          selected: heatmapIndex === selectedConfidenceScoreIndex,
          confidence: confidence,
          isColumnSelector: false,
        };
      });
      localRows.push(localRow);
    });

    setRowData(localRows);
  }, [
    selectedTable,
    selectedPageNumber,
    selectedConfidenceScoreIndex,
    selectedTableTypeColumnTypes,
    numColumns,
  ]);

  const formatter = useCallback(
    ({ value }: { value: CellValue }) => {
      const heatmapIndex = getHeatmapIndex(value.confidence / 100);
      const style: React.CSSProperties = {};
      let title = `${value.value || "\u00A0"}\n\nConfidence: ${Math.floor(
        value.confidence
      )}%`;
      if (!value.isColumnSelector) {
        style.background = `${confidenceHeatmapRange[heatmapIndex].color}`;
      }
      if (value.isColumnSelector && !value.columnTypes) {
        title = "Identify table type before identifying columns";
      } else if (value.isColumnSelector) {
        title = "Identify column type";
      }
      return (
        <div className="custom-cell-content" title={title} style={style}>
          {value.value || "\u00A0"}
        </div>
      );
    },
    [confidenceHeatmapRange]
  );

  const dataGridColumns = useMemo(() => {
    return Array.from({ length: numColumns }, (x, i) => i).map(
      (index: number) => ({
        key: `${index}`,
        name: `Column ${index + 1}`,
        formatter: formatter,
        editor: CustomTextAndSelectEditor,
        resizable: true,
      })
    );
  }, [numColumns, formatter]);

  if (selectedTable === undefined) {
    return null;
  }

  const column1Actions = [
    {
      icon: <span className="glyphicon glyphicon-remove" />,
      callback: () => {
        alert("Locate");
      },
    },
    {
      icon: "glyphicon glyphicon-link",
      actions: [
        {
          text: "Option 1",
          callback: () => {
            alert("Option 1 clicked");
          },
        },
        {
          text: "Option 2",
          callback: () => {
            alert("Option 2 clicked");
          },
        },
      ],
    },
  ];

  function getCellActions(column: DataGrid.Column<any>, row: any) {
    const cellActions = new Map();
    cellActions.set("1", column1Actions);

    console.log(`${cellActions}`);

    return column1Actions;
  }

  const handleCellSelect = (e: { rowIdx: number; idx: number }) => {
    if (e.rowIdx >= 1) {
      setSelectedTag(selectedTable.rows[e.rowIdx - 1][e.idx]);
    }
  };

  const handleCellDeselect = (e: { rowIdx: number; idx: number }) => {
    setSelectedTag({ tag: undefined });
  };

  return (
    <TableGridContainer className="ag-theme-alpine">
      <DataGrid
        columns={dataGridColumns}
        rowGetter={(i) => rowData[i]}
        rowsCount={rowData.length}
        minHeight={1000}
        // getCellActions={getCellActions}
        rowRenderer={({ renderBaseRow, ...props }) => {
          return renderBaseRow({ ...props, cellRenderer: CustomCell });
        }}
        onGridRowsUpdated={({
          fromRow,
          toRow,
          action,
          updated,
          ...otherProps
        }) => {
          const updatedValues = updated as {
            [columnName: string]: string;
          };
          // Only handle cell updates (no cell drags)
          if (action.toLowerCase().indexOf("update") === -1) {
            return;
          }
          // @ts-ignore - react-data-grid typings are outdated
          const updatedRowData = otherProps.fromRowData as RowData;
          for (let i = fromRow; i < toRow + 1; i++) {
            Object.keys(updatedValues).forEach((columnName) => {
              const cell = updatedRowData[columnName];
              const updatedValue = updatedValues[columnName];
              const columnIndex = dataGridColumns.findIndex(
                ({ key }) => key === columnName
              );
              if (columnIndex === -1) {
                return;
              }

              if (cell.isColumnSelector) {
                setTableColumnType({
                  columnIndex,
                  columnType: updatedValue,
                });
              } else {
                // If there is a column selection row, offset the row index by 1
                // const rowIndex = selectedTableTypeColumnTypes ? i - 1 : i;
                const rowIndex = i - 1;
                updateTableCell({
                  pageNumber: selectedPageNumber,
                  table: selectedTableIndex,
                  row: rowIndex,
                  column: columnIndex,
                  value: `${updatedValue}`,
                });
              }
            });
          }
        }}
        enableCellSelect={true}
        onCellSelected={(e) => {
          handleCellSelect(e);
        }}
        onCellDeSelected={(e) => {
          handleCellDeselect(e);
        }}
      />
    </TableGridContainer>
  );
};

export default () => {
  return (
    <TableViewContainer>
      <TableHeader />
      <TableGrid />
    </TableViewContainer>
  );
};
