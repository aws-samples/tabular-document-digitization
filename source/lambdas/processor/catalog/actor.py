# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from shared.defines import *
from shared.environ import *
from shared.helpers import *

from shared.document import Document
from shared.storage  import S3Uri
from shared.message  import Message
from shared.bus      import Bus

from utils import ExcelHelper

def lambda_handler(event, context):
    
    helper   = ExcelHelper()
    document = Document.from_dict(event)
    message  = Message(document.DocumentID)

    message.DocumentID            = document.DocumentID
    message.MapUpdates.StageS3Uri = S3Uri(Bucket = STORE_BUCKET, Prefix = f'{STAGE}/{document.DocumentID}')

    try :

        Logger.info(f'{STAGE} Actor : Started Processing DocumentID = {document.DocumentID}')

        for n, humanAnswer in enumerate(document.AugmentMap.StageS3Uri.List()):
            xlsxContent = helper.convert(humanAnswer.GetJSON())
            S3Uri(Bucket = STORE_BUCKET, Object = f'{STAGE}/{document.DocumentID}/{n}.xlsx').Put(xlsxContent)

        Logger.info(f'{STAGE} Actor : Stopped Processing DocumentID = {document.DocumentID}')

    except (

    ) as e :

        Logger.info(f'{STAGE} Actor : Errored Processing DocumentID = {document.DocumentID} > {str(e)}')

        message.ActorGrade = Grade.FAIL
        message.FinalStamp = GetCurrentStamp()

    else :

        message.ActorGrade = Grade.PASS
        message.FinalStamp = GetCurrentStamp()

    Bus.PutMessage(stage = STAGE, message_body = message.to_json())

    return None

if  __name__ == '__main__':

    STAGE = Stage.CATALOG

    document = Document.from_dict(
        {
            'DocumentID' : '123',
            'StageState' : 'Catalog#Running',
            'AugmentMap' :
            {
                'PrimaryHLN' : 'something',
                'StageS3Uri' :
                {
                    'Bucket' : STORE_BUCKET,
                    'Prefix' : 'augment/123/primary'
                }
            }
        }
    ).to_dict()
    
    lambda_handler(document, None)
