# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from shared.defines import *
from shared.loggers import Logger
from shared.clients import LambdaClient

class Action:

    @staticmethod
    def Invoke(function_name, payload_bytes = b''):

        print(f'Action Invoking Function = {function_name}')

        response = LambdaClient.invoke(
            FunctionName   = function_name,
            Payload        = payload_bytes,
            InvocationType = 'Event' # expecting StatusCode of 202 for Event type
        )

        if  response['StatusCode'] != 202:
            Logger.pretty(response)

        return PASS if response['StatusCode'] == 202 else \
               FAIL
