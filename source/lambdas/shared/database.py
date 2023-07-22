# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from boto3.dynamodb.conditions import Key

from shared.defines import *
from shared.environ import *
from shared.loggers import Logger
from shared.clients import DynamoDBResource, Key

from shared.document import Document

class Database:
    """
    Database Abstraction Layer
    """

    Table = DynamoDBResource.Table(TABLE_PIPELINE)

    Logger.info(f'Database Connecting! : DynamoDB Resource is {TABLE_PIPELINE}')

    @staticmethod
    def GetDocument(document_id: str) -> Document:
        """
        Fetch a specific document
        """

        document_id = document_id.lower()

        try:
            response = Database.Table.get_item(Key = {'DocumentID': document_id})
        except Exception as e:

            response = None

            Logger.info(
                f'Database GetDocument : document_id = {document_id} : exception = {e}'
            )

        if (
            response and
            response.get('Item') and
            response['ResponseMetadata']['HTTPStatusCode'] == 200
        ):
            return Document.from_dict(response['Item'])
        else:
            return None

    @staticmethod
    def GetDocuments(stages: List[Stage], states: List[State]) -> List[Document]:
        """
        Fetch a specific document set
        """

        for stage in stages:
            for state in states:

                response = Database.Table.query(
                    IndexName              = INDEX_PROGRESS,
                    KeyConditionExpression = Key('StageState').eq(f'{stage}{HASH}{state}'.title())
                )

                for item in response['Items']:
                    yield Document.from_dict(item)
        return []

    @staticmethod
    def PutDocument(document: Document) -> Document:
        """
        Update a specific document
        """
        document.DocID = document.DocID.lower()
        
        response = Database.Table.put_item(Item = document.to_dict())

        Logger.info(
            f'Database.PutDocument : DocumentID = {document.DocumentID}'
        )

        return PASS if response['ResponseMetadata']['HTTPStatusCode'] == 200 else \
               FAIL

    @staticmethod
    def PromoteDocument(currentStage: Stage, nextStage: Stage):
        """
        Promote documents in SUCCESS state from current stage to next stage WAITING state
        """

        for documentToUpdate in Database.GetDocuments([currentStage], [State.SUCCESS]):

            Logger.info(f'Moving {documentToUpdate} stage to {nextStage}')

            documentToUpdate.Stage = nextStage
            documentToUpdate.State = State.WAITING

            Database.PutDocument(documentToUpdate)

if __name__ == '__main__':

    document = Database.GetDocument(document_id = 'd000')

    if  document:

        document.CurrentMap.RetryCount += 1
        document.CurrentMap.InputS3Uri  = 's3://bucket/acquire/something.pdf'
        document.Stage                  = Stage.CONVERT
        document.State                  = State.WAITING
        document.DocumentID             = '100'

      # Database.PutDocument(document)
