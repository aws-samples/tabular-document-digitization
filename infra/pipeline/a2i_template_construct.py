# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path
from uuid    import uuid4

from aws_cdk import aws_iam, aws_lambda, aws_logs, Duration, CustomResource, Aws
from aws_cdk.custom_resources import (
    Provider,
)
from constructs import Construct

class A2ITemplateConstruct(Construct):
    def __init__(
            self,
            scope         : Construct,
            prefix        : str,
            template_name : str,
            template_path : str
    ) -> None:

        super().__init__(scope, template_name)

        self.__template_name = template_name
        self.__template_path = template_path

        self.__prefix        = prefix

        lambda_role = aws_iam.Role(
            scope      = self,
            id         = f'{self.__prefix}-srole-creator-template',
            assumed_by = aws_iam.ServicePrincipal('lambda.amazonaws.com'),
        )

      # allow us to fetch worker template from s3 and call sagemaker APIs.
        lambda_role.add_to_policy(
            statement = aws_iam.PolicyStatement(
                resources = ['*'],
                actions   = [
                    'lambda:InvokeFunction',
                    's3:*',
                    'sagemaker:*',
                    'logs:CreateLogGroup',
                    'logs:CreateLogStream',
                    'logs:PutLogEvents',
                ],
            )
        )

        lambda_path = str(Path(__file__).parent.joinpath('custom_resource_manager/').absolute())

        lambda_func = aws_lambda.Function(
            scope         = self,
            id            = f'{self.__prefix}-creator-template',
            function_name = f'{self.__prefix}-creator-template',
            code          = aws_lambda.Code.from_asset(lambda_path),
            handler       = 'a2i_template_manager.lambda_handler',
            runtime       = aws_lambda.Runtime.PYTHON_3_8,
            timeout       = Duration.minutes(15),
            memory_size   = 3000,
            role          = lambda_role,
        )

        provider = Provider(
            scope            = self,
            id               = f'{self.__prefix}-provider-template',
            on_event_handler = lambda_func
        )

      # ideally grab the worker template file hash from the frontend deploy step, but currently
      # there doesn't appear to be a way to grab that. so instead just always rebuild the
      # worker template even if it deletes and recreates the same resource.

        self.__template_resource = CustomResource(
            self,
            self.__template_name,
            service_token = provider.service_token,
            properties    =
            {
                'WorkerTemplateS3Uri' : self.__template_path,
                'HumanTaskUiName'     : self.__template_name,
                'WorkerTemplateHash'  : str(uuid4()),
            })

    def get_template_arn(self):

        return f'arn:aws:sagemaker:{Aws.REGION}:{Aws.ACCOUNT_ID}:human-task-ui/{self.__template_name}'

    def get_template_resource(self):

        return self.__template_resource
