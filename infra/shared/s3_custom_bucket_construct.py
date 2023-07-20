# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path

import jsii
from aws_cdk import aws_lambda, aws_s3, Duration, CustomResource
from aws_cdk.custom_resources import Provider
from constructs import Construct


@jsii.implements(aws_s3.IBucket)
class S3CustomBucketConstruct(aws_s3.Bucket):

    def __init__(
            self,
            scope: Construct,
            bucket_name: str,
            id: str,
            recursive_object_removal: bool = False,
            **kwargs
    ) -> None:
        super().__init__(scope = scope, id = id, bucket_name = bucket_name, **kwargs)

        if recursive_object_removal:

            lambda_path = str(Path(__file__).parent.joinpath('custom_resource_manager/').absolute())

            lambda_func = aws_lambda.Function(
                scope         = scope,
                id            = f'{id}-s3-object-remover-lambda',
                function_name = f'{bucket_name}-object-remover'[1:20],
                code          = aws_lambda.Code.from_asset(lambda_path),
                handler       = 's3_custom_bucket_manager.lambda_handler',
                runtime       = aws_lambda.Runtime.PYTHON_3_8,
                timeout       = Duration.minutes(15),
                memory_size   = 3000
            )

            provider = Provider(
                scope            = scope,
                id               = f'{id}-object-remover-provider',
                on_event_handler = lambda_func
            )

            deletion_resource = CustomResource(
                scope         = scope,
                id            = f'{id}-object-remover-resource',
                service_token = provider.service_token,
                properties    = {"bucket": self.bucket_name}
            )

            self.grant_delete(lambda_func)
            self.grant_read(lambda_func)

            deletion_resource.node.add_dependency(self)
