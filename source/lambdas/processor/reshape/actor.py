# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from shared.defines import *
from shared.environ import *
from shared.loggers import Logger
from shared.helpers import GetCurrentStamp
from shared.message import ReshapeMapUpdates
from shared.clients import TextractClient, S3Client

from shared.document import Document
from shared.storage  import S3Uri
from shared.bus      import Bus

from traceback import print_exc
from typing    import List, Dict, Tuple
from dotmap    import DotMap

from utils     import TextractHelper

def lambda_handler(event: Dict, context):
    """
    Worker for converting output textract analyze-document identified 'TABLE' items to a new
    format usable by the user interface

    Event format: shared.document.Document
    }
    """

    helper   = TextractHelper()

    document = Document.from_dict(event)
    message  = ReshapeMapUpdates(DocumentID = document.DocumentID)

    Logger.info(f'{STAGE} Actor : Started Processing DocumentID = {document.DocumentID}')

    textract_id   = document.ExtractMap.TextractID
    source_s3_uri = document.ExtractMap.StageS3Uri
    output_s3_uri = S3Uri(Bucket = STORE_BUCKET, Object = f'{STAGE}/{document.DocumentID}/humanInTheLoop.json')

    try:
        Logger.info(f'{STAGE} Actor : Working on Textract JobID = {document.ExtractMap.TextractID}')

        try:
            
            textract_response = helper.get_result_from_s3(textract_id, source_s3_uri.Bucket, source_s3_uri.Prefix.rstrip(textract_id))
            task_input        = helper.reshape(textract_response, document_uri = document.ConvertMap.StageS3Uri.Url)

        except:

            Logger.error(
                f'{STAGE} Actor : Error Processing Textract Results from S3 for Textract JobID = {document.ExtractMap.TextractID}'
            )

            textract_response = helper.get_result_from_api(textract_id)
            task_input        = helper.reshape(textract_response, document_uri = document.ConvertMap.StageS3Uri.Url)

        Logger.info(
            f'{STAGE} Actor : Reshaped Results into Task-Input Format for Textract JobID = {document.ExtractMap.TextractID}'
        )

        output_s3_uri.PutJSON(task_input)

    except Exception as e:

        print_exc()

        Logger.error(
            f'{STAGE} Actor : Errored Processing DocumentID = {document.DocumentID} > {str(e)}'
        )

        message.ActorGrade = FAIL

    message.MapUpdates.StageS3Uri = output_s3_uri
    message.FinalStamp            = GetCurrentStamp()

    Bus.PutMessage(stage = STAGE, message_body = message.to_json())

    Logger.info(f'{STAGE} Actor : Stopped Processing DocumentID = {document.DocumentID}')

if  __name__ == '__main__':

    STAGE = Stage.RESHAPE

    document = Document.from_dict(
        {
            'DocumentID' : 'd001',
            'StageState' : 'Reshape#Running',
            'ExtractMap' :
            {
                'TextractID' : 'f2092f86fc6de1010f9c87ef0dda5c9d76ff41991d5ad017f8264536cdcf0dba',
                'StageS3Uri' :
                {
                    'Bucket' : 'tdd-ips-store-document-980451951626-us-east-1',
                    'Prefix' : 'extract/d001/f2092f86fc6de1010f9c87ef0dda5c9d76ff41991d5ad017f8264536cdcf0dba'
                }
            }
        }
    ).to_dict()

    lambda_handler(document, None)
