# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from shared.defines import *
from shared.environ import *
from shared.loggers import Logger

from shared.database import Database
from shared.document import Document
from shared.storage  import S3Uri
from shared.machine  import Machine
from shared.bus      import Bus

from os.path import splitext

def ingestDocumentFromS3(notification):

  # future enhancement: add manifest file to ingest documents, which can contain other meta information such as priority and
  # multiple sub-pages of a single document etc
  # future enhancement: add service api to ingest documents

    """
    {
        "document_id" : "xxx-1234-ab",
        "priority_level": 1,
        "source":
        [
            "s3://<bucket>/*.jpg",
            "s3://<bucket>/something_a.jpg",
            "s3://<bucket>/something_3.jpg",
        ]
    }
    """

    bucket       = notification['s3']['bucket']['name']
    object       = notification['s3']['object']['key']
    create_stamp = notification['eventTime']
    priority     = object.split('/')[1] if object.count('/') > 1 else '0' # initial priority
    document_id  = splitext(object.split('/')[-1])[0]

   #"<bucket>/acquire/<initial_priority>/<document_id>.pdf"
    
    document = Document(DocumentID = document_id)

    document.Stage = Stage.ACQUIRE
    document.State = State.WAITING
    document.Order = priority
    document.Stamp = create_stamp

    document.AcquireMap.StageS3Uri = S3Uri(Bucket = bucket, Object = object)

    Logger.info(f'S3 Trigger : Ingesting New DocumentID = {document.DocumentID}, Priority = {document.Order}')

    Database.PutDocument(document)

def lambda_handler(event, context):

    for record in event.get('Records', []):

        ingestDocumentFromS3(notification = record)

    Machine.RunDatabase()

    return None

if  __name__ == '__main__':

  # S3 -> LM -> DB -> SF:[ AQ > CU > EX > RE > OP > AU > CT]

    lambda_handler(
        event =
        {
            'Records': [
                {
                'eventVersion': '2.0',
                'eventSource': 'aws:s3',
                'awsRegion': 'us-east-1',
                'eventTime': '1970-01-01T00:00:00.000Z',
                'eventName': 'ObjectCreated:Put',
                'userIdentity': {
                    'principalId': 'EXAMPLE'
                },
                'requestParameters': {
                    'sourceIPAddress': '127.0.0.1'
                },
                'responseElements': {
                    'x-amz-request-id': 'EXAMPLE123456789',
                    'x-amz-id-2': 'EXAMPLE123/5678abcdefghijklambdaisawesome/mnopqrstuvwxyzABCDEFGH'
                },
                's3': {
                    's3SchemaVersion': '1.0',
                    'configurationId': 'testConfigRule',
                    'bucket': {
                    'name': 'tdd-acquire-store-document-980451951626-us-east-1',
                    'ownerIdentity': {
                        'principalId': 'EXAMPLE'
                    },
                    'arn': 'arn:aws:s3:::example-bucket'
                    },
                    'object': {
                    'key': 'acquire/1/001.pdf',
                    'size': 1024,
                    'eTag': '0123456789abcdef0123456789abcdef',
                    'sequencer': '0A1B2C3D4E5F678901'
                    }
                }
                }
            ]
        },
        context = None
    )
