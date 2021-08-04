# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from typing  import List, Dict
from pathlib import Path

from aws_cdk import (
    core, aws_lambda
)

class Manager:
    STARTUP = 'startup'
    PROMOTE = 'promote'
    BREAKUP = 'breakup'
    RESTART = 'restart'
    PROCESS = 'process'
    CHECKUP = 'checkup'
    STANDBY = 'standby'

class PipelineManagerConstruct(core.Construct):
    def __init__(
        self,
        scope  : core.Construct,
        id     : str,
        prefix : str,
        layers : List[aws_lambda.LayerVersion],
        source : Path,
        common : Dict,
        **kwargs,
    ) -> None:

        super().__init__(scope = scope, id = id, **kwargs)

        self.__scope  = scope
        self.__prefix = prefix
        self.__source = source
        self.__layers = layers
        self.__common = common

        self.__manager_lambdas = {}

        self.__create_startup_lambda()
        self.__create_breakup_lambda()
        self.__create_restart_lambda()
        self.__create_promote_lambda()

    def get_manager_lambdas(self):
        """
        Returns constructed management lambda functions
        {
            'restart' : aws_lambda.Function
            'startup' : aws_lambda.Function
            'breakup' : aws_lambda.Function
            'promote' : aws_lambda.Function
        }
        """

        return self.__manager_lambdas

    def __create_startup_lambda(self):

        self.__manager_lambdas[Manager.STARTUP] = self.__create_lambda_function(Manager.STARTUP, {})

    def __create_breakup_lambda(self):

        self.__manager_lambdas[Manager.BREAKUP] = self.__create_lambda_function(Manager.BREAKUP, {})

    def __create_restart_lambda(self):
        self.__manager_lambdas[Manager.RESTART] = self.__create_lambda_function(Manager.RESTART, {})

    def __create_promote_lambda(self):
        self.__manager_lambdas[Manager.PROMOTE] = self.__create_lambda_function(Manager.PROMOTE, {})

    def __create_lambda_function(self, manager, environ):

        environment = dict(self.__common)
        environment.update(environ)

        lambda_function = aws_lambda.Function(
            scope         = self.__scope,
            id            = f'{self.__prefix}-manager-{manager}',
            function_name = f'{self.__prefix}-manager-{manager}',
            code          = aws_lambda.Code.from_asset(f'{self.__source}/manager/{manager}'),
            handler       = 'handler.lambda_handler',
            runtime       = aws_lambda.Runtime.PYTHON_3_8,
            timeout       = core.Duration.minutes(15),
            memory_size   = 3000,
            environment   = environment,
        )

        for dependency_layer in self.__layers :
            lambda_function.add_layers(dependency_layer)

        return lambda_function
