# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from shared.defines import *
from shared.environ import *
from shared.helpers import *

from shared.database import Database
from shared.document import Document
from shared.storage  import S3Uri
from shared.message  import Message
from shared.bus      import Bus

from utils import ImageHelper

def lambda_handler(event, context):

    document = Document.from_dict(event)
    message  = Message(DocumentID = document.DocumentID)

    try:

        Logger.info(f'{STAGE} Actor : Started Processing DocumentID = {document.DocumentID}')

        sourceS3Uri = document.AcquireMap.StageS3Uri
        outputS3Uri = S3Uri(
            Bucket = STORE_BUCKET,
            Object = f'{STAGE}/{document.DocumentID}/{document.DocumentID}.pdf'
        )

        if  sourceS3Uri.FileType != 'pdf':

            outputBlob = ImageHelper(imageBytes = sourceS3Uri.Get()).convert(outputType = 'pdf')

        else:

            outputBlob = sourceS3Uri.Get()

        outputS3Uri.Put(outputBlob) # copy document over

        message.MapUpdates.StageS3Uri = outputS3Uri
        message.FinalStamp            = GetCurrentStamp()
        message.ActorGrade            = Grade.PASS

        Logger.info(f'{STAGE} Actor : Stopped Processing DocumentID = {document.DocumentID}')

    except (

    ) as e:

        message.ActorGrade = Grade.FAIL

        Logger.info(f'{STAGE} Actor : Errored Processing DocumentID = {document.DocumentID}')

    Bus.PutMessage(stage = STAGE, message_body = message.to_json())

    return None


if  __name__ == '__main__':

    STAGE = Stage.CONVERT

    document = Document.from_dict(
        {
            'DocumentID' : 'd000',
            'StageState' : 'Convert#Running',
            'AcquireMap' :
            {
                'StageS3Uri' :
                {
                    'Bucket' : f'{STORE_BUCKET}',
                    'Object' : 'acquire/p0/d000.png'
                }
            }
        }
    ).to_dict()    

    lambda_handler(document, None)
