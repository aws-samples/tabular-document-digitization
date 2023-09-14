# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

"""
Performs a conversion from a Tabular-HIL document to an excel file.

Tabular-HIL is the input and output of the Augment (UI) stage.

Can be run locally to test on sample files:
    python3 tabular_hil_to_excel_converter.py <sample_file>
"""


from tempfile import TemporaryFile
from io import BytesIO

from pandas   import DataFrame, ExcelWriter

class ExcelHelper:

    def convert(self, document, output = None):
        """Converts from the input dictionary of HIL document format to an excel file."""
        output = BytesIO()

        writer = ExcelWriter(output, engine = 'xlsxwriter')

        for page_ind, page in enumerate(document.get('pages', [])):
            for table_ind, table in enumerate(page.get('tables', [])):
                title = self.tableToTitle(page_ind, table_ind, table)
                df    = self.tableToDf(table)

                if  df is None:
                    continue

                df.to_excel(writer, sheet_name = title, header = False, index = False)

        writer.close()

        return output.getvalue()

    def parseHeader(self, headerColumnTypes, numCols):
        """Generate a header from the given column types and number of columns"""
        header = [''] * numCols
        for i in range(numCols):
            headerType = headerColumnTypes.get(str(i),'')
            if (headerType != ''):
                header[i] = headerType

        return header

    def parseRows(self, rows):
        """Create a flat list of rows with text/editedText as needed"""

        outputRows = []
        for row in rows:
            newRow = []
            for col in row:
                text = col.get('editedText', col.get('text', ''))
                newRow.append(text)
            outputRows.append(newRow)

        return outputRows

    def tableToDf(self, table):
        """Convert a single table in the input format to a pandas dataframe."""

        rows = self.parseRows(table.get('rows', []))

        # We don't know the number of columns without at least one row existing.
        if len(rows) == 0:
            return None

        numCols = len(rows[0])

        header = self.parseHeader(table.get('headerColumnTypes', []), numCols)
        
        flat_table = [header, *rows]
        df = DataFrame(flat_table)

        return df

    def tableToTitle(self, pageInd, tableInd, table):
        """Get a title for the table."""

        tableType = table.get('tableType', 'unknown')
        return f'{pageInd+1}.{tableInd+1}-type-{tableType}'

if  __name__ == '__main__':

    import argparse
    import json

    parser = argparse.ArgumentParser(
        description = 'Convert from tabular hil format to excel file'
    )
    
    parser.add_argument('file', metavar='M', help='Input tabular hil formatted file')

    args = parser.parse_args()
    outputPath = 'output.xlsx'

    helper = ExcelHelper()

    with open(args.file) as f:
        result = helper.convert(json.loads(f.read()), outputPath)

    with open(outputPath, "wb") as f:
        f.write(result)

    print(f'Wrote to {outputPath}')
