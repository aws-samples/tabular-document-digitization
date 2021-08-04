# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from shared.environ import *
from shared.loggers import Logger
from shared.clients import StepFunctionsClient

class Manager:

    STARTUP = 'startup'
    CHECKUP = 'checkup'
    BREAKUP = 'breakup'
    RESTART = 'restart'
    PROMOTE = 'promote'
    STANDBY = 'standby'

class Machine:

    @staticmethod
    def GetLastExecutedDatabaseStep(executionArn):

        execution_histories = StepFunctionsClient.get_execution_history(executionArn = executionArn,
                                                                        reverseOrder = True)
        last_executed_step = next(
            history['stateEnteredEventDetails']
            for history in execution_histories['events'] if 'stateEnteredEventDetails' in history)

        return last_executed_step['name']

    @staticmethod
    def RunDatabase():
        '''
        Start State Machine Execution
        - StartExecution is idempotent for same input + name combination.
        '''
        # Results are sorted by time, with the most recent execution first
        # https://docs.aws.amazon.com/step-functions/latest/apireference/API_ListExecutions.html

        executions = StepFunctionsClient.list_executions(
            stateMachineArn = STATE_PIPELINE_ARN,
            maxResults      = 1
        )['executions']

        trigger_step_function = True

        for execution in executions:
            if  execution['status'] == 'RUNNING':
                while True:
                    last_executed_step = Machine.GetLastExecutedDatabaseStep(execution['executionArn'])
                    if last_executed_step == Manager.BREAKUP:
                        break
                    elif last_executed_step == Manager.CHECKUP:
                        continue
                    else:
                        trigger_step_function = False
                        break

        if  trigger_step_function:
            step_function_execution_name = 0

            if  len(executions) > 0:

                step_function_execution_name = int(executions[0]['name']) + 1

            StepFunctionsClient.start_execution(
                stateMachineArn = STATE_PIPELINE_ARN,
                input           = '{}',
                name            = f'{step_function_execution_name:05}',
                traceHeader     = PREFIX
            )
        else:
            
            Logger.info(
                f'Three is a running step Function already being executed {executions[0]} so Skipping.'
            )
