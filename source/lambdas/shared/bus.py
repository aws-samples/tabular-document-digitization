# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from shared.defines import *
from shared.environ import *
from shared.loggers import Logger
from shared.clients import SQSResource, ServiceResource


class Bus:

    Queue = {}

    def GetQueue(stage) -> ServiceResource:

        if  stage.lower() not in Bus.Queue:

            queue_name = f'{PREFIX}-queue-{stage}'.lower()

            Logger.info(f'Bus : Getting Queue {queue_name} by Name')

            Bus.Queue[stage.lower()] = SQSResource.get_queue_by_name(
                QueueName = queue_name
            )

        return Bus.Queue[stage.lower()]

    def GetMessages(stage = STAGE):

        while True:

            response = Bus.GetQueue(stage).receive_messages(MaxNumberOfMessages = 10)

            for message in response:
                yield message

            if  len(response) == 0:
                break

    def DelMessages(stage = STAGE, receipt_handles = []):

        response = Bus.GetQueue(stage).delete_messages(Entries = receipt_handles)

        return PASS if response else FAIL

    def PutMessage(stage = STAGE, message_body = '', message_attributes = {}):

        response = Bus.GetQueue(stage).send_message(
            MessageBody       = message_body,
            MessageAttributes = message_attributes
        )

        return PASS if response else FAIL

    def Purge(stage = STAGE):

        try:
        
            Bus.GetQueue(stage).purge()

        except:

            for message in Bus.GetMessages(stage = stage):
                message.delete()

if  __name__ == '__main__':

    for message in Bus.GetMessages(stage = STAGE):
        message.delete()

    for n in range(20):
        Bus.PutMessage(
            stage = STAGE, message_body = dumps({'DocumentID': f'{n:03d}', 'Status': PASS})
        )
