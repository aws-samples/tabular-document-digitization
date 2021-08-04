# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from shared.defines import *
from shared.environ import *
from shared.helpers import *

from shared.processor import BeginProcessor
from shared.database  import Database
from shared.action    import Action
from shared.bus       import Bus

def lambda_handler(event, context):

    BeginProcessor(stage = STAGE, actor = STAGE_ACTOR, retryLimit = 30).process()

if  __name__ == '__main__':

    lambda_handler({}, None)
