# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from shared.clients import TextractClient, S3Client
from shared.storage import S3Uri
from typing         import List, Dict

class TextractHelper:

    def get_result_from_s3(cls, textract_id: str, s3_bucket:str, s3_prefix: str) -> Dict:

        from textractcaller.t_call import get_full_json_from_output_config, OutputConfig

        textract_response = get_full_json_from_output_config(OutputConfig(s3_bucket = s3_bucket,
                                                                          s3_prefix = s3_prefix),
                                                                          job_id    = textract_id,
                                                                          s3_client = S3Client)

        return textract_response

    def get_result_from_api(cls, textract_id) -> Dict:

        from textractcaller.t_call import get_full_json, Textract_API


        textract_response = get_full_json(job_id                = textract_id,
                                          textract_api          = Textract_API.ANALYZE,
                                          boto3_textract_client = TextractClient)

        return textract_response

    def reshape(cls, textract_response: List[Dict],
                document_uri = 's3://bucket/prefix/document.pdf',
                table_types  = [{'name' : 'Table'},
                                {'name' : 'Form', 'columnTypes' : ['Key', 'Value']}]) -> Dict:

        assert textract_response.get('JobStatus') == 'SUCCEEDED'
        assert textract_response.get('Blocks'   ) != None

      # https://github.com/aws-samples/amazon-textract-response-parser/blob/master/src-python/README.md
        from trp import Document as TextractDocument
        
        document   = TextractDocument(textract_response)

        task_input = {
            'numPages'   : len(document.pages),
            'pages'      : [],
            'tableTypes' : table_types,
            'metadata'   : { 'sourceDocumentUrl' : document_uri}
        }

        def getPair(field, f, p):
            if  not field.value:
                print(f'Warning ﹕ Missing Field Value → KEY = {field.key.text}')

            return [
                {
                    'text'        : field.key.text.strip(':').strip(),
                    'confidence'  : field.key.confidence,
                    'boundingBox' : {
                                        'top'    : field.key.geometry.boundingBox.top,
                                        'left'   : field.key.geometry.boundingBox.left,
                                        'width'  : field.key.geometry.boundingBox.width,
                                        'height' : field.key.geometry.boundingBox.height
                                    },
                    'tag'       : f'p{p:02d}-form-f{f:02d}-key'
                },
                {
                    'text'        : field.value.text.strip(),
                    'confidence'  : field.value.confidence,
                    'boundingBox' : {
                                        'top'    : field.value.geometry.boundingBox.top,
                                        'left'   : field.value.geometry.boundingBox.left,
                                        'width'  : field.value.geometry.boundingBox.width,
                                        'height' : field.value.geometry.boundingBox.height
                                    },
                    'tag'       : f'p{p:02d}-form-f{f:02d}-value'                
                } if field.value else { 'text' : '-- NO VALUE DETECTED --'}
            ]

        def getForm(form, p): # convert key-value pairs detected on page into special 2-column table
            return {'tableType' : 'Form', 'headerColumnTypes'  : ['Key', 'Value'], 'rows' : sorted([getPair(field, f, p) for f, field in enumerate(form.fields)], key = lambda field: field[0]['boundingBox']['top'])}

        def getTable(table, t, p):

            return {'tableType' : 'Table', 'headerColumnTypes' : [], 'rows' : [getRow(row, r, t, p) for r, row in enumerate(table.rows)] }

        def getRow(row, r, t, p):

            return [{ 'text'      : cell.text.strip(),
                    'confidence'  : cell.confidence,
                    'boundingBox' : {
                                        'top'    : cell.geometry.boundingBox.top,
                                        'left'   : cell.geometry.boundingBox.left,
                                        'width'  : cell.geometry.boundingBox.width,
                                        'height' : cell.geometry.boundingBox.height
                                    },
                    'tag'         : f'p{p:02d}-t{t:02d}-r{r:02d}-c{c:02d}' } for c, cell in enumerate(row.cells)]

        for p, page in enumerate(document.pages):

            task_input['pages'].append({ 'pageNumber' : p + 1, 'tables' : [] })

            for t, table in enumerate(page.tables):
                task_input['pages'][p]['tables'].append(getTable(table, t, p))
                
            if  len(page.form.fields) > 0:
                task_input['pages'][p]['tables'].append(getForm(page.form, p))

        return task_input
