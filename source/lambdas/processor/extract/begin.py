# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from shared.defines import *
from shared.environ import *
from shared.helpers import GetCurrentStamp, GetEnvVar
from shared.loggers import Logger
from shared.clients import TextractClient

from shared.database import Database
from shared.document import Document
from shared.storage  import S3Uri

from shared.processor import BeginProcessor

class ExtractBeginProcessor(BeginProcessor):

    def extractTables(self, document: Document):

        try:

            document.CurrentMap.StageS3Uri = S3Uri(Bucket = STORE_BUCKET, Prefix = f'{STAGE}/{document.DocumentID}')

            response = TextractClient.start_document_analysis(
            **{
                'DocumentLocation' :
                {
                    'S3Object' :
                    {
                        'Bucket' : document.ConvertMap.StageS3Uri.Bucket,
                        'Name'   : document.ConvertMap.StageS3Uri.Object,
                    }
                },
                'FeatureTypes' :
                [
                    'TABLES',
                ],
                'NotificationChannel' :
                {
                    'RoleArn'     : GetEnvVar('SROLE_TEXTRACT_ARN'),
                    'SNSTopicArn' : GetEnvVar('TOPIC_TEXTRACT_ARN'),
                },
                'ClientRequestToken' : str(uuid4()),
                'OutputConfig' :
                {
                    'S3Bucket' : document.CurrentMap.StageS3Uri.Bucket,
                    'S3Prefix' : document.CurrentMap.StageS3Uri.Prefix,
                },
                'JobTag': document.DocumentID,
            })

        except (
            TextractClient.exceptions.ProvisionedThroughputExceededException,
            TextractClient.exceptions.LimitExceededException
        ) as e:

            return FAIL, None

        return PASS, response

    def processDocuments(self):

        rateLimited = False

        for document in Database.GetDocuments(stages = [self.stage], states = [State.HOLDING, State.WAITING]):

            status, result = self.extractTables(document)

            if  status == PASS:

                Logger.info(
                    f'{self.stage} Begin Processor : Calling Textract for DocumentID = {document.DocumentID}, Submission = PASS'
                )

                Logger.pretty(result)

                document.State                 = State.RUNNING
                document.CurrentMap.StartStamp = GetCurrentStamp()
                document.CurrentMap.TextractID = result['JobId']
                document.CurrentMap.StageS3Uri = S3Uri(Bucket = STORE_BUCKET, Prefix = f'{STAGE}/{document.DocumentID}/{document.CurrentMap.TextractID}')

            else:

                Logger.info(
                    f'{self.stage} Begin Processor : Calling Textract for DocumentID = {document.DocumentID}, Submission = FAIL'
                )

                document.State                  = State.HOLDING
                document.CurrentMap.RetryCount += 1

                rateLimited = True

            Database.PutDocument(document)

            if  rateLimited:
                break

def lambda_handler(event, context):


    ExtractBeginProcessor(stage = STAGE, actor = None, retryLimit = 5).process()

if  __name__ == '__main__':

    STAGE = Stage.EXTRACT

    Database.PutDocument(Document.from_dict(
        {
            'DocumentID' : '123',
            'StageState' : 'Extract#Waiting',
            'ConvertMap' :
            {
                'StageS3Uri' :
                {
                    'Bucket' : STORE_BUCKET,
                    'Object' : 'convert/123/cleaned.png'
                }
            }
        }
    ))

    S3Uri(Bucket = STORE_BUCKET, Object = 'convert/123/cleaned.png').Put(open('sample/000.png', 'rb').read())

    lambda_handler({}, None)
