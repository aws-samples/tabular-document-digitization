# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from aws_cdk import (
    core,
    aws_s3,
    aws_s3_deployment,
)

from pathlib import Path

from infra.shared.s3_custom_bucket_construct import S3CustomBucketConstruct


class TemplateStack(core.Stack):

    def __init__(
            self,
            scope  : core.Construct,
            id     : str,
            prefix : str,
            suffix : str,
            source : Path,
            bucket : aws_s3.Bucket = None,
            **kwargs
    ) -> None:

        super().__init__(scope, id, **kwargs)

        self.__prefix = prefix
        self.__suffix = suffix
        self.__source = source

        self.__bucket_name = f'{self.__prefix}-store-resource-{self.__suffix}'

        self.__bucket = bucket or S3CustomBucketConstruct(
            scope                    = self,
            id                       = self.__bucket_name,
            bucket_name              = self.__bucket_name,
            block_public_access      = aws_s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy           = core.RemovalPolicy.DESTROY,
            recursive_object_removal = True
        )

        # this prefix is used to generate liquid {{ s3://... | grant_read_access }} tags inside
        # the worker template during the 'npm run build-hitl' step.

        self.__assets_path = f'.assets/{self.__source.name}'
        self.__assets_uri  = f's3://{self.__bucket_name}/{self.__assets_path}'

        print(self.__assets_uri)

        environ = {
            'S3_PREFIX' : self.__assets_uri,
        }

        bundler = {
            'image'      : core.BundlingDockerImage.from_registry('node:lts'),
            'user'       : 'root',
            'environment': environ,
            'command'    :
            [
                'bash',
                '-c',
                '&&'.join(
                    [
                        'npm install',
                        'npm run build-hitl',
                        'cp -R build/* /asset-output/',
                    ]
                ),
            ],
        }

        self.__assets_bundle = aws_s3_deployment.Source.asset(
            path     = str(source),
            bundling = bundler
        )

      # deploy the worker template bundle to s3
        aws_s3_deployment.BucketDeployment(
            scope                  = self,
            id                     = f'{self.__prefix}-{self.__source.name}-deploy',
            sources                = [self.__assets_bundle],
            destination_bucket     = self.__bucket,
            destination_key_prefix = self.__assets_path,
        )

    def get_resources(self):
        """
        all resources other stacks might be interested in leveraging
        """

        return {
            'liquid_uri' : f'{self.__assets_uri}/worker-template.liquid.html'
        }
