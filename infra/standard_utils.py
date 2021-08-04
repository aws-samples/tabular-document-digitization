# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from hashlib import md5
from    json import loads
from      os import popen, getenv

class Env:

    def GetAccount():

        result = loads(popen('aws sts get-caller-identity --output json').read() or '{}')

        return result.get('Account', 'error').strip()

    def GetRegion():

        result = popen('aws configure get region --output text').read() or 'error'

        return result.strip()

    def GetDeploy():

        branch = popen('git rev-parse --abbrev-ref HEAD').read().strip() or 'error'
        deploy = getenv('DEPLOY', branch).title().replace('_', '').replace('-', '')

        return deploy

    def GetPrefix():

        deploy = Env.GetDeploy()
        
        return f'tdd-{deploy}'.lower()

    def GetSuffix():

        account = Env.GetAccount()
        region  = Env.GetRegion()
        suffix  = f'{account}-{region}'

        return suffix.lower()

    def GetUnique():

        suffix  = Env.GetSuffix()
        hashed  = md5(suffix.encode()).hexdigest()

        return hashed