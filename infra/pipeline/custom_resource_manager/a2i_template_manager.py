# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from urllib.parse import urlparse
from boto3        import client, resource

client = client('sagemaker')
s3     = resource('s3')


def uri_to_s3_obj(s3_uri):
    s3_uri_parsed = urlparse(s3_uri)
    return s3.Object(s3_uri_parsed.netloc, s3_uri_parsed.path.lstrip('/'))


def fetch_s3(s3_uri):
    print(f'FETCH {s3_uri}')
    obj = uri_to_s3_obj(s3_uri)

    exit_loop = False

    while not exit_loop:
        try:
            body = obj.get()['Body']
            exit_loop = True
        except s3.meta.client.exceptions.NoSuchKey:
            print('no such key in bucket. Waiting')

    return body.read()


def lambda_handler(event, context):
    
    request_type = event['RequestType']
    
    if request_type == 'Create': return on_create(event)
    if request_type == 'Update': return on_update(event)
    if request_type == 'Delete': return on_delete(event)

    raise Exception('Invalid request type: %s' % request_type)

def on_create(event):
    props = event['ResourceProperties']
    print('create new resource with props %s' % props)
    worker_template = fetch_s3(props['WorkerTemplateS3Uri']).decode('utf-8')
    print('Fetched worker_template: ', worker_template)

    name = props['HumanTaskUiName']
    response = client.create_human_task_ui(
        HumanTaskUiName = name,
        UiTemplate = {
            'Content': worker_template
        },
    )
    print('Create worker template response: ', response)

  # add your create code here...
    physical_id = name

    return {'PhysicalResourceId': physical_id}


def on_update(event):
  # delete and re-create but keep the name the same.
    on_delete(event)
    return on_create(event)


def on_delete(event):
    physical_id = event['PhysicalResourceId']

    response = client.delete_human_task_ui(
        HumanTaskUiName = physical_id
    )
    print(response)
