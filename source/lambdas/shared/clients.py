# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from boto3                     import resource, client
from boto3.dynamodb.conditions import Key
from boto3.resources.base      import ServiceResource

DynamoDBResource    = resource('dynamodb')
CloudWatchResource  = resource('cloudwatch')
SQSResource         = resource('sqs')
S3Resource          = resource('s3')

StepFunctionsClient = client('stepfunctions')
A2IClient           = client('sagemaker-a2i-runtime')
CloudWatchClient    = client('cloudwatch')
LogsClient          = client('logs')
TextractClient      = client('textract')
DynamoDBClient      = client('dynamodb')
LambdaClient        = client('lambda')
SQSClient           = client('sqs')
S3Client            = client('s3')
