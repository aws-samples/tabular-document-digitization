# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import json
from typing import Dict, List
from shared.clients import S3Client, S3Resource

from dataclasses import asdict, dataclass, fields, _MISSING_TYPE

@dataclass
class S3Uri:
    Bucket: str = ''
    Object: str = ''
    Prefix: str = ''

    @property
    def Key(self):
        return self.Object

    @property
    def Url(self):
        return f's3://{self.Bucket}/{self.Object or self.Prefix}'

    @property
    def FileName(self):
        return self.Object.split('/')[-1].split('.')[0]

    @property
    def FileType(self):
        return self.Object.split('/')[-1].split('.')[-1]

    def Get(self) -> bytearray:
        
        response = S3Resource.Object(bucket_name = self.Bucket, key = self.Key).get()

        return response['Body'].read()

    def GetText(self) -> str:

        return self.Get().decode('utf-8')

    def GetJSON(self) -> Dict:
        
        return json.loads(self.GetText())

    def Put(self, body : bytearray = b'', contentType = 'application/octet-stream'):

        S3Resource.Object(bucket_name = self.Bucket, key = self.Key).put(Body = body, ContentType = contentType)

    def PutJSON(self, body : Dict = {}):

        self.Put(json.dumps(body).encode(), contentType = 'application/json')

    def List(self, key_predicate = lambda x : True) -> List['S3Uri']:

        params = {'Bucket' : self.Bucket, 'Prefix' : self.Prefix}

        while True:
            response = S3Client.list_objects_v2(**params)

            for object in [o for o in response.get('Contents', []) if key_predicate(o['Key'])]:
                yield S3Uri(Bucket = self.Bucket, Object = object['Key'])

            params['ContinuationToken'] = response.get('NextContinuationToken')

            if  not params['ContinuationToken'] :
                break

    @classmethod
    def FromUrl(cls, url: str):

        b,o = url.lower().strip('s3://').split('/', 1)

        return cls(Bucket = b, Object = o)
