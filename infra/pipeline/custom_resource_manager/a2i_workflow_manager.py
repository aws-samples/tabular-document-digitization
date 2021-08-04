# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from time  import sleep
from boto3 import client

client = client('sagemaker')

def lambda_handler(event, context):

    print(event)

    request_type = event['RequestType']

    if  request_type == 'Create': return on_create(event)
    if  request_type == 'Update': return on_update(event)
    if  request_type == 'Delete': return on_delete(event)

    raise Exception('Invalid request type: %s' % request_type)

def on_create(event):

    props    = event['ResourceProperties']

    response = client.create_flow_definition(
        FlowDefinitionName = props['FlowDefinitionName'],
        HumanLoopConfig    =
        {
            'WorkteamArn'     : props['WorkteamArn'],
            'HumanTaskUiArn'  : props['HumanTaskUiArn'],
            'TaskTitle'       : props['TaskTitle'],
            'TaskDescription' : props['TaskDescription'],
            'TaskCount'       : int(props['TaskCount'])
        },
        RoleArn            = props['RoleArn'],
        OutputConfig       =
        {
            'S3OutputPath' : props['S3OutputPath']
        }
    )
    print('Create worker flow definition response: ', response)

    physical_id = props['FlowDefinitionName']
    return {'PhysicalResourceId': physical_id}


def on_update(event):

  # delete and re-create but keep the name the same.
    on_delete(event)
    return on_create(event)


def on_delete(event):

    props = event['ResourceProperties']

    while True:
        try :
            print('Deleting : ' + props['FlowDefinitionName'])
            response = client.delete_flow_definition(FlowDefinitionName = props['FlowDefinitionName'])
            sleep(5)
        except client.exceptions.ResourceNotFound :
            break
