# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from shared.defines import *
from shared.environ import *
from shared.helpers import *

from shared.processor import AwaitProcessor

def lambda_handler(event, context):

    AwaitProcessor(stage = STAGE, timeoutMinutes = 30).process()

if  __name__ == '__main__':

    lambda_handler({}, None)
