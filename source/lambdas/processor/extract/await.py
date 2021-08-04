# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from shared.defines import *
from shared.environ import *
from shared.helpers import *

from shared.bus       import Bus
from shared.message   import Message
from shared.database  import Database
from shared.processor import AwaitProcessor

class TextractStatus:
    SUCCEEDED = 'SUCCEEDED'

class ExtractAwaitProcessor(AwaitProcessor):

    def extractTextractResponse(self, message):

        pass

    def processCallbackEvents(self):

        """
        Process completion events from asynchronous requests coming through the stage event bus.
        """

        for wrapper in Bus.GetMessages(stage = self.stage):

            response = DotMap(**loads(wrapper.body))
            message  = DotMap(**loads(response.Message))
            document = Database.GetDocument(document_id = message.JobTag)

            if  not document:

                Logger.info(
                    f'{self.stage.title()} Await Processor : Received Callback for DocumentID = {message.JobTag}, Unable to Find in Database'
                )
                wrapper.delete()
                continue

            if  message.Status == TextractStatus.SUCCEEDED:

                document.State = State.SUCCESS

                self.extractTextractResponse(message)
                self.processCallbackEventsMore(message)

                document.CurrentMap.FinalStamp = GetCurrentStamp()

                Logger.info(
                    f'{self.stage.title()} Await Processor : Received TEXTRACT Callback for DocumentID = {message.JobTag}, Status is PASS'
                )

            else:

                document.State                 = State.FAILURE
                document.CurrentMap.FinalStamp = GetCurrentStamp()

                self.processCallbackEventsMore(message)

                Logger.info(
                    f'{self.stage.title()} Await Processor : Received TEXTRACT Callback for DocumentID = {message.JobTag}, Status is FAIL'
                )

            Database.PutDocument(document)

            wrapper.delete()

def lambda_handler(event, context):

    ExtractAwaitProcessor(stage = STAGE, timeoutMinutes = 30).process()

if  __name__ == '__main__':

    STAGE = Stage.EXTRACT

    Bus.PutMessage(stage = STAGE,
        message_body = dumps(
        {
            'Type'             : 'Notification',
            'MessageId'        : '7ef19000-6bae-5e22-99de-c879cdec171d',
            'TopicArn'         : 'arn:aws:sns:us-east-1:980451951626:tdd-prime-topic-textract',
            'Message'          : '{"JobId":"47a93838bd49752082f8ba6a14cc1bdc741506a443019055ac5181cf78ff6827","Status":"SUCCEEDED","API":"StartDocumentAnalysis","JobTag":"008","Timestamp":1610589186182,"DocumentLocation":{"S3ObjectName":"cleanup/008/document.png","S3Bucket":"tdd-prime-store-document-980451951626-us-east-1"}}',
            'Timestamp'        : '2021-01-14T01:53:06.249Z',
            'SignatureVersion' : '1',
            'Signature'        : 'SUbXQQBsW/AUdlM+lyug1Nc4Par7jRRh9DBXIVAQu6UJXRJ0CkUnUCNrOpJ1uWnmEA69w+GuRgxIVT1G8iqWfeqMtyZIVLeqQDB0rvgdmAX7mQuzA48JcVWS7CLe0qQKwQ8HbaxzCw+GvfzBXCABuXnJiZmwariLdkrrXtFXykHkEgxdpiM/eKgSFoXBn5zBYJXtSzSgXauImN6Sa5v83kHxE8YV5a0AMGx1zurFpZf/MxQvXc1OMydFJvhq9yWnGNIHvClYN1HIsQ2i98g9Df5AiCA6e39ucul64UKuJfRfUqgRvlMth5j8QaVDJOT5W/j3kzcRHZzEEfe33tH1og==',
            'SigningCertURL'   : 'https://sns.us-east-1.amazonaws.com/SimpleNotificationService-010a507c1833636cd94bdb98bd93083a.pem',
            'UnsubscribeURL'   : 'https://sns.us-east-1.amazonaws.com/?Action=Unsubscribe&SubscriptionArn=arn:aws:sns:us-east-1:980451951626:tdd-prime-topic-textract:7923441f-bc91-41a0-95f5-5b2bbdfb9eb9'
        })
    )

    lambda_handler({}, None)
