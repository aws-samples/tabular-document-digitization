# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from typing  import List
from pathlib import Path
from boto3   import client

from aws_cdk import (
    core, aws_sqs, aws_lambda, aws_sns, aws_sns_subscriptions, aws_iam, aws_events, aws_events_targets
)

from .a2i_workflow_construct import A2IWorkflowConstruct
from .a2i_template_construct import A2ITemplateConstruct

class Process:
    ACQUIRE = 'acquire'
    AUGMENT = 'augment'
    CATALOG = 'catalog'
    CONVERT = 'convert'
    EXTRACT = 'extract'
    OPERATE = 'operate'
    RESHAPE = 'reshape'

class Aspect:
    BEGIN = 'begin'
    ACTOR = 'actor'
    AWAIT = 'await'

class PipelineProcessConstruct(core.Construct):

    def __init__(
        self,
        scope  : core.Construct,
        id     : str,
        prefix : str,
        common : dict,
        layers : List[aws_lambda.LayerVersion],
        source : Path,
        liquid,
        bucket,
        **kwargs,
    ) -> None:

        super().__init__(scope = scope, id = id, **kwargs)

        self.__scope  = scope
        self.__prefix = prefix

        self.__common = common
        self.__source = source
        self.__layers = layers
        self.__bucket = bucket
        self.__liquid = liquid

        self.__stage_queues = {}
        self.__stage_topics = {}
        self.__stage_begin_lambdas = {}
        self.__stage_actor_lambdas = {}
        self.__stage_await_lambdas = {}

        self.__create_stage_acquire(stage = Process.ACQUIRE)
        self.__create_stage_convert(stage = Process.CONVERT)
        self.__create_stage_extract(stage = Process.EXTRACT)
        self.__create_stage_reshape(stage = Process.RESHAPE)
        self.__create_stage_operate(stage = Process.OPERATE)
        self.__create_stage_augment(stage = Process.AUGMENT)
        self.__create_stage_catalog(stage = Process.CATALOG)

    def get_stage_actor_lambdas(self):
        """
        Returns the constructed lambda functions
        Example Returned object (These are the Async Lambda Functions)
        {
            'acquire'    : aws_lambda.Function
            'augment'    : aws_lambda.Function
            'catalog'    : aws_lambda.Function
            .
            .
        }
        """

        return self.__stage_actor_lambdas

    def get_stage_await_lambdas(self):
        """
        Returns the constructed lambda functions
        Example Returned object (These are the Await Lambda Functions)
        {
            'acquire' : aws_lambda.Function
            'augment' : aws_lambda.Function
            'catalog' : aws_lambda.Function
            .
            .
        }
        """

        return self.__stage_await_lambdas

    def get_stage_begin_lambdas(self):
        """
        Returns the constructed lambda functions
        Example Returned object (These are the Begin Lambda Functions)
        {
            'acquire' : aws_lambda.Function
            'augment' : aws_lambda.Function
            'catalog' : aws_lambda.Function
            .
            .
        }
        """

        return self.__stage_begin_lambdas

    def __get_work_teams(self):
        sagemaker = client("sagemaker")
        paginator = sagemaker.get_paginator("list_workteams")
        workteams = set()
        for page in paginator.paginate():
            for workteam in page["Workteams"]:
                workteams.add(workteam["WorkteamName"])

        return workteams


    def __create_stage_acquire(self, stage):

        queue = self.__create_queue(stage)

        self.__create_actor_lambda(stage, queue)
        self.__create_begin_lambda(stage, queue)
        self.__create_await_lambda(stage, queue)

    def __create_stage_augment(self, stage):

        queue = self.__create_queue(stage)

        self.__create_actor_lambda(stage, queue)
        self.__create_begin_lambda(stage, queue)
        self.__create_await_lambda(stage, queue)

        template_resource = A2ITemplateConstruct(
            scope         = self,
            prefix        = self.__prefix,
            template_name = f'{self.__prefix}-a2i-template',
            template_path = self.__liquid
        )

        commons = self.node.try_get_context('ENVIRONMENTS')

        if  len(commons['WORK_TEAM_NAMES']) == 0:
            raise Exception('Make sure you have have added created work team name in the cdk.json: ENVIRONMENTS')

        allowed_workflow_resource_arns = []
        work_teams = self.__get_work_teams()

        for workteam in commons['WORK_TEAM_NAMES']:
            if workteam not in work_teams :
                raise Exception(f'Work team : {workteam} you have added does not exist in your account Make sure to '
                                'create work team from aws console.')

            workteam_arn = f'arn:aws:sagemaker:{core.Aws.REGION}:{core.Aws.ACCOUNT_ID}:workteam/private-crowd/{workteam}'

          # Custom HumanReview Workflow Resource
            workflow_resource = A2IWorkflowConstruct(
                scope             = self,
                workflow_name     = f'{self.__prefix}-wflow-{workteam}',
                prefix            = self.__prefix,
                template_resource = template_resource,
                s3_output_path    = self.__bucket.s3_url_for_object(f'augment/.a2i'),
                workteam_arn      = workteam_arn,
                task_count        = 1,
                task_description  = f'Review Tables from Source Document - {workteam.title()}',
                task_title        = f'Tabular Document Digitization'
            )

            allowed_workflow_resource_arns.append(workflow_resource.get_workflow_arn())

            self.__stage_begin_lambdas[Process.AUGMENT].add_environment(
                f'WFLOW_A2I_{workteam.upper()}_ARN', workflow_resource.get_workflow_arn()
            )

        self.__stage_begin_lambdas[Process.AUGMENT].role.add_managed_policy(
            aws_iam.ManagedPolicy.from_aws_managed_policy_name('AmazonSageMakerFullAccess')
        )

        human_review_event_pattern = aws_events.EventPattern(
            source      = ['aws.sagemaker'],
            detail_type = ['SageMaker A2I HumanLoop Status Change'],
            detail     = {
                'flowDefinitionArn': allowed_workflow_resource_arns
            }
        )

        rule = aws_events.Rule(scope         = self,
                               id            = f'{self.__prefix}-human-review-complete',
                               event_pattern = human_review_event_pattern)
        
        rule.add_target(target = aws_events_targets.SqsQueue(queue = queue))

    def __create_stage_catalog(self, stage):

        queue = self.__create_queue(stage)

        self.__create_actor_lambda(stage, queue)
        self.__create_begin_lambda(stage, queue)
        self.__create_await_lambda(stage, queue)

    def __create_stage_convert(self, stage):

        queue = self.__create_queue(stage)

        self.__create_actor_lambda(stage, queue)
        self.__create_begin_lambda(stage, queue)
        self.__create_await_lambda(stage, queue)

    def __create_stage_extract(self, stage):

        queue = self.__create_queue(stage)

        self.__create_actor_lambda(stage, queue)
        self.__create_begin_lambda(stage, queue)
        self.__create_await_lambda(stage, queue)

        # Create Textract output notification SNS topic
        topic_textract = self.__create_topic('textract')

        # Create Textract service role
        srole_textract = aws_iam.Role(
            scope      = self,
            id         = f'{self.__prefix}-srole-textract',
            assumed_by = aws_iam.ServicePrincipal('textract.amazonaws.com') # Allow role to be assumed by textract
        )

        # Allow Textract service role to publish output to Textract SNS topic
        topic_textract.grant_publish(srole_textract)

        srole_textract.grant_pass_role(self.__stage_begin_lambdas[Process.EXTRACT])

        self.__stage_begin_lambdas[Process.EXTRACT].role.add_managed_policy(
            aws_iam.ManagedPolicy.from_aws_managed_policy_name('AmazonTextractFullAccess')
        )

        self.__stage_await_lambdas[Process.EXTRACT].role.add_managed_policy(
            aws_iam.ManagedPolicy.from_aws_managed_policy_name('AmazonTextractFullAccess')
        )

        # Pass role to begin lambda
        self.__stage_begin_lambdas[Process.EXTRACT].add_environment(
            'SROLE_TEXTRACT_ARN', srole_textract.role_arn
        )

        # Pass output SNS to begin lambda
        self.__stage_begin_lambdas[Process.EXTRACT].add_environment(
            'TOPIC_TEXTRACT_ARN', topic_textract.topic_arn
        )

        # Add subscription between the Textract output SNS topic and Extract stage SQS message bus
        topic_textract.add_subscription(
            aws_sns_subscriptions.SqsSubscription(queue)
        )

    def __create_stage_operate(self, stage):

        queue = self.__create_queue(stage)

        self.__create_actor_lambda(stage, queue)
        self.__create_begin_lambda(stage, queue)
        self.__create_await_lambda(stage, queue)

    def __create_stage_reshape(self, stage):

        queue = self.__create_queue(stage)

        self.__create_actor_lambda(stage, queue)
        self.__create_begin_lambda(stage, queue)
        self.__create_await_lambda(stage, queue)

        self.__stage_await_lambdas[Process.RESHAPE].role.add_managed_policy(
            aws_iam.ManagedPolicy.from_aws_managed_policy_name('AmazonTextractFullAccess')
        )

    def __create_queue(self, stage):

        self.__stage_queues[stage] = aws_sqs.Queue(

            scope      = self.__scope,
            id         = f'{self.__prefix}-queue-{stage}',
            queue_name = f'{self.__prefix}-queue-{stage}',
        )

        return self.__stage_queues[stage]

    def __create_topic(self, stage):

        self.__stage_topics[stage] = aws_sns.Topic(
            scope      = self,
            id         = f'{self.__prefix}-topic-{stage}',
            topic_name = f'{self.__prefix}-topic-{stage}'
        )

        return self.__stage_topics[stage]

    def __create_begin_lambda(self, stage, queue):

        actor = self.__stage_actor_lambdas[stage]

        environ = {
            'STAGE'       : stage,
            'STAGE_QUEUE' : queue.queue_name,
            'STAGE_ACTOR' : actor.function_name,
        }

        lambda_function = self.__create_lambda_function(stage, Aspect.BEGIN, environ)

      # Grant IAM Permission to begin lambda to execute actor lambda
        actor.grant_invoke(lambda_function)

        self.__stage_begin_lambdas[stage] = lambda_function

    def __create_actor_lambda(self, stage, queue):

        environ = {
            'STAGE'       : stage,
            'STAGE_QUEUE' : queue.queue_name,
        }

        lambda_function = self.__create_lambda_function(stage, Aspect.ACTOR, environ)

        queue.grant_send_messages(lambda_function)

        self.__stage_actor_lambdas[stage] = lambda_function

    def __create_await_lambda(self, stage, queue):

        environ = {
            'STAGE'       : stage,
            'STAGE_QUEUE' : queue.queue_name,
        }

        lambda_function = self.__create_lambda_function(stage, Aspect.AWAIT, environ)

        queue.grant_consume_messages(lambda_function)
        queue.grant(lambda_function, "sqs:*")

        self.__stage_await_lambdas[stage] = lambda_function

    def __create_lambda_function(self, stage, aspect, environ):

        environment = self.__common.copy()
        environment.update(environ)

        lambda_function = aws_lambda.Function(
            scope         = self.__scope,
            id            = f'{self.__prefix}-processor-{stage}-{aspect}',
            function_name = f'{self.__prefix}-processor-{stage}-{aspect}',
            code          = aws_lambda.Code.from_asset(f'{self.__source}/processor/{stage}'),
            handler       = f'{aspect}.lambda_handler',
            runtime       = aws_lambda.Runtime.PYTHON_3_8,
            timeout       = core.Duration.minutes(15),
            memory_size   = 3000,
            environment   = environment
        )

        for dependency_layer in self.__layers :
            lambda_function.add_layers(dependency_layer)

        return lambda_function
