# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from shared.environ import STORE_BUCKET
from shared.loggers import Logger
from shared.clients import S3Resource, S3Client

class Store:

    @staticmethod
    def GetFile(stage = '', file_path = ''):
        """
        Get file from stage folder within the store.
        """

        key      = f'{stage}/{file_path}'
        bucket   = STORE_BUCKET

        Logger.info(f'Store Getting File : Bucket = {bucket}, Key = {key}')

        response = S3Resource(bucket_name = bucket, key = key).get()

        Logger.pretty(response)

    def PutFile(stage = '',  file_path = '', byte_string = b''):
        """
        Put file into stage folder within the store.
        """

        key      = f'{stage}/{file_path}'
        bucket   = STORE_BUCKET

        Logger.info(f'Store Putting File : Bucket = {bucket}, Key = {key}')

        response = S3Resource.Object(bucket_name = bucket, key = key).put(Body = byte_string)

        Logger.pretty(response)

        return PASS if response['ResponseMetadata']['HTTPStatusCode'] == 200 else \
               FAIL

if  __name__ == '__main__':

    Store.PutFile(stage = 'acquire', file_path = '01/001.png', byte_string = open('sample/001.png', 'rb').read())
