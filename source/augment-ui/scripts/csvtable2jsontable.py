"""
Converts a CSV file to table JSON in the format expected by this annotation tool.

Sample usage:

python scripts/csv2jsontable.py \
    --infile ./public/sample-data/SampleStatement.csv \
    --outfile ./public/sample-data/SampleStatement.json

Requires: click

$ pip install click

"""

import click
import csv
import uuid
import random
import json

@click.command()
@click.option('--infile', help='Path to input csv file. Example: --infile ./public/sample-data/SampleStatement.csv', required=True)
@click.option('--outfile', help='Path to output table json file. Example: --outfile ./public/sample-data/MySampleStatement.csv', required=True)
@click.option('--pages', type=int, default=2, help='Duplicate the output this number of times in the output table json. Useful for building test table json files.')
def main(infile, outfile, pages):
    click.echo(f"Reading input CSV {infile}")
    with open(infile) as infile_reader:
        infile_reader = csv.reader(infile_reader)
        header = next(infile_reader)
        rows = [row for row in infile_reader]
    click.echo(f"Read {len(rows)} rows from input CSV")
    click.echo(f"Building output...")
    pages = [
        {
            "Table": str(uuid.uuid4()),
            "PageNumber": page_index+1,
            "Rows" : [{
                "Row": f"{row_index+1}",
                "Cells": [
                    {
                        "Text": cell,
                        "Confidence": confidence,
                        "WordConfidence": [confidence],
                        "Column": f"{cell_index+1}"
                    } for (cell_index, cell) in enumerate(row) for confidence in [random.random()*50 + 50]
                ]
            } for (row_index,row) in enumerate(rows)]
        } for page_index in range(pages)
    ]
    output_dict = {
        "Titles": header,
        "Pages": pages
    }
    click.echo(f"Saving output to {outfile}")
    with open(outfile,"w") as outfile_writer:
        outfile_writer.write(json.dumps(output_dict,indent=4))
    
if __name__ == '__main__':
    main()