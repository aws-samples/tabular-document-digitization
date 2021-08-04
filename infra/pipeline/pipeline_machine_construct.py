# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from aws_cdk.core                    import Construct, Duration
from aws_cdk.aws_stepfunctions       import StateMachine, Task, Parallel, Choice, Condition, Wait, WaitTime
from aws_cdk.aws_stepfunctions_tasks import InvokeFunction

from .pipeline_manager_construct import (
    PipelineManagerConstruct,
    Manager
)

from .pipeline_process_construct import (
    PipelineProcessConstruct,
    Process,
    Aspect
)

from .pipeline_trigger_construct import (
    PipelineTriggerConstruct
)

class PipelineMachineConstruct(Construct):
    def __init__(
        self,
        scope   : Construct,
        id      : str,
        prefix  : str,
        pipeline_process_construct: PipelineProcessConstruct,
        pipeline_manager_construct: PipelineManagerConstruct,
        pipeline_trigger_construct: PipelineTriggerConstruct,
        **kwargs,
    ) -> None:

        super().__init__(scope, id, **kwargs)

        self.__scope  = scope
        self.__prefix = prefix

        self.__pipeline_process_construct = pipeline_process_construct
        self.__pipeline_manager_construct = pipeline_manager_construct
        self.__pipeline_trigger_construct = pipeline_trigger_construct

        self.__create_state_machine()

    def __create_state_machine(self):

        step_startup = self.__get_startup_step()
        step_promote = self.__get_promote_step()
        step_process = self.__get_process_step()
        step_breakup = self.__get_breakup_step()
        step_restart = self.__get_restart_step()
        step_checkup = self.__get_checkup_step(step_restart, step_process, step_breakup)
        step_standby = self.__get_standby_step()

        step_startup.next(step_promote).next(step_checkup)
        step_process.next(step_standby).next(step_promote)

        state_machine = StateMachine(
            scope              = self,
            id                 = f'{self.__prefix}-state-pipeline',
            state_machine_name = f'{self.__prefix}-state-pipeline',
            definition         = step_startup,
        )

        for lambda_function in self.__pipeline_trigger_construct.get_trigger_lambdas().values():
            state_machine.grant_start_execution(lambda_function)
            state_machine.grant_read(lambda_function)

    def __get_startup_step(self):

        manager_lambdas = (
            self.__pipeline_manager_construct.get_manager_lambdas()
        )

        return Task(
            scope       = self,
            id          = Manager.STARTUP,
            task        = InvokeFunction(manager_lambdas[Manager.STARTUP]),
        )

    def __get_promote_step(self):
        manager_lambdas = (
            self.__pipeline_manager_construct.get_manager_lambdas()
        )
        return Task(
            scope       = self,
            id          = Manager.PROMOTE,
            task        = InvokeFunction(manager_lambdas[Manager.PROMOTE]),
        )

    def __get_process_step(self):

        parallel_state = Parallel(
            scope = self,
            id    = 'process' 
            )

        acquire_step_begin = self.__get_process_chain(Process.ACQUIRE)
        convert_step_begin = self.__get_process_chain(Process.CONVERT)
        extract_step_begin = self.__get_process_chain(Process.EXTRACT)
        reshape_step_begin = self.__get_process_chain(Process.RESHAPE)
        operate_step_begin = self.__get_process_chain(Process.OPERATE)
        augment_step_begin = self.__get_process_chain(Process.AUGMENT)
        catalog_step_begin = self.__get_process_chain(Process.CATALOG)

        parallel_state = (
            parallel_state
            .branch(acquire_step_begin)
            .branch(convert_step_begin)
            .branch(extract_step_begin)
            .branch(reshape_step_begin)
            .branch(operate_step_begin)
            .branch(augment_step_begin)
            .branch(catalog_step_begin)
        )

        return parallel_state

    def __get_process_step_state(self, stage, aspect):

        lambda_function = \
        {
            Aspect.BEGIN : self.__pipeline_process_construct.get_stage_begin_lambdas(),
            Aspect.ACTOR : self.__pipeline_process_construct.get_stage_actor_lambdas(),
            Aspect.AWAIT : self.__pipeline_process_construct.get_stage_await_lambdas()
        }[aspect][stage]

        return Task(
            scope       = self,
            id          = f'{stage}-{aspect}',
            task        = InvokeFunction(lambda_function)
        )

    def __get_process_chain(self, stage):

        aspects       = [Aspect.BEGIN, Aspect.AWAIT]
        process_chain = self.__get_process_step_state(stage, aspects.pop(0)) # start chain from first aspect in list

        for aspect in aspects:

            process_chain.next(self.__get_process_step_state(stage, aspect))

        return process_chain

    def __get_checkup_step(self, restart_step, process_step, breakup_step):

        return (
            Choice(self, Manager.CHECKUP)
            .when(Condition.boolean_equals('$.restartPipeline', True), restart_step)
            .when(Condition.boolean_equals('$.processDocument', True), process_step)
            .otherwise(                                                breakup_step)
        )

    def __get_breakup_step(self):

        manager_lambdas = (
            self.__pipeline_manager_construct.get_manager_lambdas()
        )

        return Task(
            scope       = self,
            id          = Manager.BREAKUP,
            task        = InvokeFunction(manager_lambdas[Manager.BREAKUP])
        )

    def __get_restart_step(self):

        manager_lambdas = (
            self.__pipeline_manager_construct.get_manager_lambdas()
        )

        return Task(
            scope       = self,
            id          = Manager.RESTART,
            task        = InvokeFunction(manager_lambdas[Manager.RESTART])
        )

    def __get_standby_step(self):

        return Wait(
            scope = self,
            id    = Manager.STANDBY,
            time  = WaitTime.duration(Duration.seconds(60))
        )
