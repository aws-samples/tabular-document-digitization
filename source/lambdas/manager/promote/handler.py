# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from shared.database import Database
from shared.defines import Stage

STAGE_TRANSITIONS_ORDER = [Stage.ACQUIRE,
                           Stage.CONVERT,
                           Stage.EXTRACT,
                           Stage.RESHAPE,
                           Stage.OPERATE,
                           Stage.AUGMENT,
                           Stage.CATALOG]

def lambda_handler(context, event):
    for index in range(len(STAGE_TRANSITIONS_ORDER) - 1):
        current_stage, next_stage = STAGE_TRANSITIONS_ORDER[index], STAGE_TRANSITIONS_ORDER[index + 1]
        Database.PromoteDocument(current_stage, next_stage)

    return {
        'restartPipeline' : False,
        'processDocument' : True,
        }
