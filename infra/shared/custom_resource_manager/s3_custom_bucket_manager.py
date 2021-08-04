# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from boto3 import resource
from os import getenv

s3_resource = resource('s3')


def lambda_handler(event, context):
    print(event)

    request_type = event['RequestType']

    if request_type == 'Create':
        return {'Status': 'Created'}
    if request_type == 'Update':
        return {'Status': 'Updated'}
    if request_type == 'Delete':
        return on_delete(event)
    raise Exception('Invalid Request Type: %s' % request_type)


def on_delete(event):
    props = event["ResourceProperties"]
    print("create new resource with props %s" % props)
    bucket_name = props["bucket"]
    bucket = s3_resource.Bucket(bucket_name)

    while bucket.objects.all() and sum(1 for _ in bucket.objects.all()) > 0:
        bucket.objects.all().delete()

    return {'Status': 'Deleted'}