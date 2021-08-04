# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from shared.defines import *
from shared.environ import *
from shared.helpers import GetCurrentStamp
from shared.loggers import Logger

from shared.document import Document
from shared.storage  import S3Uri
from shared.message  import Message
from shared.bus      import Bus

from traceback import print_exc
from typing    import List

def lambda_handler(event, context):

    document = Document.from_dict(event)
    message  = Message(DocumentID = document.DocumentID)

    Logger.info(f'{STAGE} Actor : Started Processing DocumentID = {document.DocumentID}')
    
    sourceS3Uri = document.ReshapeMap.StageS3Uri
    outputS3Uri = S3Uri(Bucket = STORE_BUCKET, Object = f'{STAGE}/{document.DocumentID}/humanInTheLoop-Operated.json')

    try:

        hil_document = sourceS3Uri.GetJSON()
        
        # Example 'OPERATE' action
        hil_document['tableTypes'] = get_operate_table_types()
        # Add empty tableType and headerColumnTypes to each page table
        # (this is where A2I annotation values will go)
        for page in hil_document['pages']:
            for table in page['tables']:
                table['tableType'] = None
                table['headerColumnTypes'] = {}

        outputS3Uri.PutJSON(body = hil_document)

        Logger.info(f'{STAGE} Actor : Stopped Processing DocumentID = {document.DocumentID}')

    except Exception as e:
        
        print_exc()

        Logger.error(
            f'{STAGE} Actor : Errored Processing DocumentID = {document.DocumentID} > {str(e)}'
        )

        message.ActorGrade = FAIL
    
    message.MapUpdates.StageS3Uri = outputS3Uri
    message.FinalStamp            = GetCurrentStamp()

    Bus.PutMessage(stage = STAGE, message_body = message.to_json())

def get_operate_table_types() -> List[str]:
    """
    Sample list of column names to append to operate HIL json output
    Replace with application-specific logic.
    """
    return [
        {
            'name': 'Checking Transactions',
            'columnTypes': [
                'Date',
                'Description',
                'Transaction #',
                'Check #',
                'Amount',
                'Reference',
                'N/A'
            ]
        },
        {
            'name': 'Savings Transactions',
            'columnTypes': [
                'Date',
                'Description',
                'Transaction #',
                'Amount',
                'Reference',
                'N/A'
            ]
        },
        {
            'name': 'Statement Summary'
        },
        {
            'name': 'Statement of Net Assets',
            'columnTypes': [
                'Asset/Liability',
                'Allocated',
                'Unallocated',
                'Total',
                'N/A'
            ]
        },    ]

if  __name__ == '__main__':

    lambda_handler({'DocumentID': '001'}, None)
