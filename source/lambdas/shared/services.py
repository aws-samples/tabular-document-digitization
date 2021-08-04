# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from boto3.session import Session
from boto3 import resource, client

ddb = client("dynamodb")
a2i = client("sagemaker-a2i-runtime")
sm = client("sagemaker")
s3 = client("s3")
s3_resource = resource('s3')
sqs = client("sqs")
textract_client = client('textract')
