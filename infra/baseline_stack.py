# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from aws_cdk import (
    core,
    aws_s3,
    aws_s3_deployment,
)

from pathlib import Path

class BaselineStack(core.Stack):

    def __init__(
            self,
            scope  : core.Construct,
            id     : str,
            prefix : str,
            suffix : str,
            source : Path = None,
            **kwargs
    ) -> None:

        super().__init__(scope, id, **kwargs)

        self.__prefix = prefix
        self.__suffix = suffix
        self.__source = source

        self.__resource_bucket_name = f'{self.__prefix}-store-resource-{self.__suffix}'
        self.__document_bucket_name = f'{self.__prefix}-store-document-{self.__suffix}'
        self.__resource_bucket      = None
        self.__document_bucket      = None

        if  False:

            self.__resource_bucket = aws_s3.Bucket(
                scope               = self,
                id                  = self.__resource_bucket_name,
                bucket_name         = self.__resource_bucket_name,
                block_public_access = aws_s3.BlockPublicAccess.BLOCK_ALL,
                removal_policy      = core.RemovalPolicy.DESTROY
            )


        if  False:
            self.__document_bucket = aws_s3.Bucket(
                scope               = self,
                id                  = self.__document_bucket_name,
                bucket_name         = self.__document_bucket_name,
                block_public_access = aws_s3.BlockPublicAccess.BLOCK_ALL,
                removal_policy      = core.RemovalPolicy.DESTROY
            )        
    
    def get_resources(self):
        """
        all resources other stacks might be interested in leveraging.
        """

        return {
            'resource_bucket'      : self.__resource_bucket,
            'resource_bucket_name' : self.__resource_bucket_name,
            'document_bucket'      : self.__document_bucket,
            'document_bucket_name' : self.__document_bucket_name,
        }