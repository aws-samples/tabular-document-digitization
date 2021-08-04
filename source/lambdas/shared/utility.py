# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from shared.defines import STAGE, STORE_BUCKET

def GetS3OutputPath(document_id: str, output_filename: str = 'output.json', stage: str = STAGE) -> str:
    """Returns S3 path for output file created by Stage Actor"""
    return f's3://{STORE_BUCKET}/{stage}/{document_id}/{output_filename}'
