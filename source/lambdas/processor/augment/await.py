# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from re               import search
from urllib.parse     import urlparse
import json

from shared.bus       import Bus
from shared.database  import Database
from shared.document  import Document
from shared.document  import S3Uri
from shared.environ   import *
from shared.helpers   import *
from shared.processor import AwaitProcessor


class A2IHumanLoopStatus:
    Stopped   = 'Stopped'
    Completed = 'Completed'


class AugmentAwaitProcessor(AwaitProcessor):

    def processCallbackEvents(self):
        '''
        Process completion events from asynchronous requests coming through the stage event bus.
        '''

        for wrapper in Bus.GetMessages(stage = self.stage):

            message                        = DotMap(**loads(wrapper.body))
            message.detail                 = DotMap(**message.detail)
            message.detail.humanLoopOutput = DotMap(**message.detail.humanLoopOutput)
            message.documentID             = message.detail.humanLoopName.split('--')[1]
            document                       = Database.GetDocument(document_id = message.documentID)

            if not document:

                Logger.info(
                    f'{self.stage.title()} Await Processor : Received A2I Callback for DocumentID = {message.documentID}, '
                    f'Unable to Find in Database'
                )
                wrapper.delete()
                continue

            if  message.detail.humanLoopStatus in (A2IHumanLoopStatus.Completed, A2IHumanLoopStatus.Stopped):

                outputS3Uri = S3Uri.FromUrl(message.detail.humanLoopOutput.outputS3Uri)
                outputJSON  = outputS3Uri.GetJSON()

                flowName    = search(r':flow-definition/([^/]+)', outputJSON.get('flowDefinitionArn', '')).group(1)


                for order, humanAnswer in enumerate(outputJSON.get('humanAnswers', [])):

                    Logger.info(
                        f'{self.stage.title()} Await Processor : Received A2I Callback for DocumentID = {message.documentID}, '
                        f'Processing Human Answer from Workflow → {flowName}'
                    )
                    
                    Logger.pretty(humanAnswer, f'Human Answer {order}')

                    answerContent    =   humanAnswer.get('answerContent', {})
                    answerSubmission = answerContent.get('submission',  '{}')
                    answerTabularHIL = loads(answerSubmission)

                    S3Uri(Bucket = STORE_BUCKET,
                          Object = f'{STAGE}/{document.DocumentID}/{flowName}/{order}.json').PutJSON(answerTabularHIL)

                document.State                 = State.SUCCESS
                document.CurrentMap.FinalStamp = GetCurrentStamp()
                document.CurrentMap.StageS3Uri = S3Uri(Bucket = STORE_BUCKET,
                                                       Prefix = f'{STAGE}/{document.DocumentID}/{flowName}') # point to directory as more than one possible answer

                Logger.info(
                    f'{self.stage.title()} Await Processor : Received A2I Callback for DocumentID = {message.documentID}, '
                    f'Status is PASS'
                )

            else:

                document.State                 = State.FAILURE
                document.CurrentMap.ActorGrade = FAIL
                document.CurrentMap.Exceptions = [dumps(message.toDict(), indent = 4)]
                document.CurrentMap.FinalStamp = GetCurrentStamp()

                self.processCallbackEventsMore(message)

                Logger.info(
                    f'{self.stage.title()} Await Processor : Received A2I Callback for DocumentID = {message.documentID}, '
                    f'Status is FAIL'
                )

            Database.PutDocument(document)

            wrapper.delete()

def lambda_handler(event, context):
    AugmentAwaitProcessor(stage = STAGE, timeoutMinutes = 300).process()

if __name__ == '__main__':

    STAGE = Stage.AUGMENT

    path  = f'augment/.a2i/primary/2021/01/01/00/00/00/primary--123--2021-01-01t00-00-00-000000/output.json'

    with open('sample/000.a2i.json', 'rb') as f:
        S3Uri(Bucket = STORE_BUCKET, Object = path).Put(f.read())

    Database.PutDocument(Document.from_dict(
        {
            'DocumentID' : '123',
            'StageState' : 'Augment#Running',
            'OperateMap' :
            {
                'StageS3Uri' :
                {
                    'Bucket' : STORE_BUCKET,
                    'Object' : 'operate/123/humanInTheLoop-Operated.json'
                }
            }
        }
    ))

    Bus.PutMessage(stage        = STAGE,
                   message_body = dumps(
                       {
                           'version'       : '0',
                           'id'            : '26e93a87-5c77-aa0a-d684-5d8dcb93d004',
                           'detail-type'   : 'SageMaker A2I HumanLoop Status Change',
                           'source'        : 'aws.sagemaker',
                           'account'       : '980451951626',
                           'time'          : '2021-01-01T00:00:00Z',
                           'region'        : 'us-east-1',
                           'resources'     :
                            [
                                'arn:aws:sagemaker:us-east-1:980451951626:human-loop/primary--123--2021-01-01t00-00-00-000000'
                            ],
                           'detail'        :
                            {
                                'creationTime'      : '2021-01-01T00:00:00.000Z',
                                'failureCode'       : None,
                                'failureReason'     : None,
                                'flowDefinitionArn' : 'arn:aws:sagemaker:us-east-1:980451951626:flow-definition/primary',
                                'humanLoopArn'      : 'arn:aws:sagemaker:us-east-1:980451951626:human-loop/primary--123--2021-01-01t00-00-00-000000',
                                'humanLoopName'     : 'primary--123--2021-01-01t00-00-00-000000',
                                'humanLoopOutput'   :
                                {
                                    'outputS3Uri'   : f's3://{STORE_BUCKET}/{path}'
                                },
                                'humanLoopStatus'   : 'Completed'
                            }
                       })
                   )

    lambda_handler({}, None)
