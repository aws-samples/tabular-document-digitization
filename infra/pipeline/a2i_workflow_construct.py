# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path

from aws_cdk import core, aws_iam, aws_lambda, aws_logs
from aws_cdk.custom_resources import (
    Provider,
)

from .a2i_template_construct import A2ITemplateConstruct

class A2IWorkflowConstruct(core.Construct):

    def __init__(
            self,
            scope             : core.Construct,
            prefix            : str,
            workflow_name     : str,
            s3_output_path    : str,
            workteam_arn      : str,
            task_count        : int,
            task_description  : str,
            task_title        : str,
            template_resource : A2ITemplateConstruct,
            template_name     : str = None,
            html_template     : str = None,
            role_arn          : str = None,
            **kwargs
    ) -> None:

        super().__init__(scope = scope, id = workflow_name, **kwargs)


        self.__prefix        = prefix
        self.__workflow_name = workflow_name

        if  template_resource is None:
          # require template name and template html if we aren't passed a valid template as input
            assert template_name is not None and html_template is not None
            template_resource = A2ITemplateConstruct(scope, template_name, html_template)

        if  role_arn is None:
            role_arn = self.__get_workflow_role().role_arn

        lambda_path = str(Path(__file__).parent.joinpath('custom_resource_manager/').absolute())

        lambda_func = aws_lambda.Function(
            scope         = self,
            id            = f'{self.__prefix}-creator-workflow-{workflow_name}',
            function_name = f'{self.__prefix}-creator-workflow-{workflow_name}',
            code          = aws_lambda.Code.from_asset(lambda_path),
            handler       = 'a2i_workflow_manager.lambda_handler',
            runtime       = aws_lambda.Runtime.PYTHON_3_8,
            timeout       = core.Duration.minutes(15),
            memory_size   = 3000,
            role          = self.__get_custom_resource_creation_iam_role()
        )

        provider = Provider(
            scope            = self,
            id               = f'{self.__prefix}-workflow-provider-{workflow_name}',
            on_event_handler = lambda_func
        )

        self.__workflow_resource = core.CustomResource(
            scope         = self,
            id            = self.__workflow_name,
            service_token = provider.service_token,
            properties    =
            {
                'FlowDefinitionName': workflow_name,
                'TaskTitle'         : task_title,
                'TaskDescription'   : task_description,
                'TaskCount'         : task_count,
                'RoleArn'           : role_arn,
                'HumanTaskUiArn'    : template_resource.get_template_arn(),
                'WorkteamArn'       : workteam_arn,
                'S3OutputPath'      : s3_output_path
            })

      # ensures UI template is created before the workflow
        self.__workflow_resource.node.add_dependency(template_resource.get_template_resource())

    def get_workflow_arn(self):

        return f'arn:aws:sagemaker:{core.Aws.REGION}:{core.Aws.ACCOUNT_ID}:flow-definition/{self.__workflow_name}'

    def __get_workflow_role(self):

        role = aws_iam.Role(
            scope      = self,
            id         = f'{self.__prefix}-srole-workflow-{self.__workflow_name}',
            assumed_by = aws_iam.ServicePrincipal('sagemaker.amazonaws.com'),
        )

        role.add_to_policy(
            statement = aws_iam.PolicyStatement(
                resources = ['arn:aws:s3:::*'],
                actions = [
                    's3:GetObject',
                    's3:PutObject',
                    's3:DeleteObject',
                    's3:ListBucket',
                ],
            )
        )

        return role

    def __get_custom_resource_creation_iam_role(self):

        lambda_role = aws_iam.Role(
            scope      = self,
            id         = f'{self.__prefix}-srole-creator-workflow',
            assumed_by = aws_iam.ServicePrincipal('lambda.amazonaws.com'),
        )

        lambda_role.add_to_policy(
            statement = aws_iam.PolicyStatement(
                effect = aws_iam.Effect.ALLOW,
                actions = [
                    'logs:CreateLogGroup',
                    'logs:CreateLogStream',
                    'logs:PutLogEvents',
                ],
                resources = ['*']
            )
        )

        lambda_role.add_to_policy(
            statement = aws_iam.PolicyStatement(
                effect    = aws_iam.Effect.ALLOW,
                actions   = ['sagemaker:CreateFlowDefinition',
                             'sagemaker:DeleteFlowDefinition'],
                resources = ['*'],
            )
        )

        lambda_role.add_to_policy(
            statement = aws_iam.PolicyStatement(
                effect    = aws_iam.Effect.ALLOW,
                actions   = ['IAM:PassRole'],
                resources = ['*']
            )
        )

        return lambda_role
