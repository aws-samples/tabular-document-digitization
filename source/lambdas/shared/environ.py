# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from shared.helpers import GetEnvVar, GetAccount, GetRegion, GetPrefix, GetBranch

# region Load Dependencies

if  'source' in __file__: # executing locally, mock environment variables

    ACCOUNT = GetEnvVar('ACCOUNT', default = GetAccount()).lower()
    REGION  = GetEnvVar( 'REGION', default =  GetRegion()).lower()
    PREFIX  = GetEnvVar( 'PREFIX', default =  GetPrefix()).lower()
    BRANCH  = GetEnvVar( 'BRANCH', default =  GetBranch()).lower()
    STAGE   = GetEnvVar(  'STAGE', default =    'acquire').lower()

else:

    ACCOUNT = GetEnvVar('ACCOUNT', default = 'INVALID').lower()
    REGION  = GetEnvVar( 'REGION', default = 'INVALID').lower()
    PREFIX  = GetEnvVar( 'PREFIX', default = 'INVALID').lower()
    BRANCH  = GetEnvVar( 'BRANCH', default = 'INVALID').lower()    
    STAGE   = GetEnvVar(  'STAGE', default = 'INVALID').lower()

# endregion

# region Construct Resource Names

TABLE_PIPELINE  = f'{PREFIX}-table-pipeline'.lower()
INDEX_PROGRESS  = f'{PREFIX}-index-progress'.lower()
STORE_BUCKET    = f'{PREFIX}-store-document-{ACCOUNT}-{REGION}'.lower()
STAGE_QUEUE     = f'{PREFIX}-queue-{STAGE}'.lower()
STAGE_ACTOR     = f'{PREFIX}-processor-{STAGE}-actor'.lower()

STATE_PIPELINE_ARN = f'arn:aws:states:{REGION}:{ACCOUNT}:stateMachine:{PREFIX}-state-pipeline'

# endregion

def ARN(name, service = 'sns'):
    return f'arn:awn:{service}:{REGION}:{ACCOUNT}:{name}'

# environment variable name for a2i flow definition arn
ENV_A2I_FLOW_DEFINITION_ARN = 'TDD_A2I_FLOW_DEFINITION_ARN'
