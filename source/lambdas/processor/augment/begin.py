# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from shared.defines import *
from shared.environ import *
from shared.helpers import Sanatize, GetCurrentStamp, GetEnvVar
from shared.loggers import Logger
from shared.clients import A2IClient

from shared.database import Database
from shared.document import Document
from shared.storage  import S3Uri

from shared.processor import BeginProcessor

WFLOW_A2I_PRIMARY_ARN = GetEnvVar('WFLOW_A2I_PRIMARY_ARN', f'arn:aws:sagemaker:{REGION}:{ACCOUNT}:flow-definition/tdd-prime-wflow-primary')
WFLOW_A2I_QUALITY_ARN = GetEnvVar('WFLOW_A2I_QUALITY_ARN', f'arn:aws:sagemaker:{REGION}:{ACCOUNT}:flow-definition/tdd-prime-wflow-quality')


class AugmentBeginProcessor(BeginProcessor):

    def augmentTables(self, document: Document, flowDefinitionArn = WFLOW_A2I_PRIMARY_ARN):

        try:

            humanLoops     = A2IClient.list_human_loops(FlowDefinitionArn = flowDefinitionArn, MaxResults = self.maxPendingLoops)['HumanLoopSummaries']
            flowDefinition = flowDefinitionArn.split('/')[-1]
            flowName       = flowDefinition.split('wflow-')[-1]

            if  len(list(humanLoop for humanLoop in humanLoops if humanLoop['HumanLoopStatus'] == 'InProgress')) >= self.maxPendingLoops:

                return SKIP, None

          # for humanLoop in humanLoops:
          #     Logger.pretty(humanLoop, message = 'Found Human Loop')

            document.CurrentMap.StageS3Uri = S3Uri(Bucket = STORE_BUCKET, Prefix = f'{STAGE}/.a2i/{flowDefinition}')

            humanLoopTime = Sanatize(GetCurrentStamp())
            humanLoopID   = Sanatize(document.DocumentID)
            humanLoopName = Sanatize(f'{flowName}--{humanLoopID}--{humanLoopTime}').lower()

            response = A2IClient.start_human_loop(
            **{
                'HumanLoopName'     : humanLoopName,
                'FlowDefinitionArn' : flowDefinitionArn,
                'HumanLoopInput'    :
                {
                    'InputContent'  : document.OperateMap.StageS3Uri.GetText()
                },
                'DataAttributes'    :
                {
                    'ContentClassifiers':
                    [
                        'FreeOfAdultContent',
                    ]
                }
            })
        
        except (
            A2IClient.exceptions.ServiceQuotaExceededException,
            A2IClient.exceptions.ThrottlingException
        ) as e:
            return SKIP, None
        except (

        ) as e:
            return FAIL, None

        return PASS, response

    def processDocuments(self):

        rateLimited = False

        for document in Database.GetDocuments(stages = [self.stage], states = [State.HOLDING, State.WAITING]):

            status, result = self.augmentTables(document)

            if  status == PASS:

                Logger.info(
                    f'{self.stage} Begin Processor : Calling Textract for DocumentID = {document.DocumentID}, Submission = {status}'
                )

                Logger.pretty(result)

                document.State                 = State.RUNNING
                document.CurrentMap.StartStamp = GetCurrentStamp()
                document.CurrentMap.PrimaryHLA = result['HumanLoopArn']

            else:

                Logger.info(
                    f'{self.stage} Begin Processor : Calling Textract for DocumentID = {document.DocumentID}, Submission = {status}'
                )

                document.State                  = State.HOLDING
                document.CurrentMap.RetryCount += 1

                rateLimited = True

            Database.PutDocument(document)

            if  rateLimited:
                break

def lambda_handler(event, context):

    AugmentBeginProcessor(stage = STAGE, actor = None, retryLimit = 5, maxPendingLoops = 5).process()
