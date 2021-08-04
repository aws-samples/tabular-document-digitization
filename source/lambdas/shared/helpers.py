# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0


from      sys import modules
from       os import getenv, popen, times
from     json import loads
from datetime import datetime
from       re import sub

from shared.defines import *
from shared.loggers import Logger

def Sanatize(text:str, alternate = '', length = 63) -> str:

    text = str(text)
    text = sub('[_:;.+]', alternate, text)
    text = text[0:length]
    
    return text

def GetCurrentStamp():

    return datetime.now().isoformat(sep = 'T', timespec = 'seconds')

def GetAccount():

    result = loads(popen('aws sts get-caller-identity').read() or '{}')

    return result.get('Account', 'ERROR')

def GetRegion():

    result = popen('aws configure get region').read() or 'us-east-1'

    return result.strip()

def GetPrefix():

    branch = popen('git rev-parse --abbrev-ref HEAD').read().strip().replace('_','').lower()
    
    return f'tdd-{GetBranch()}'

def GetBranch():

    return popen('git rev-parse --abbrev-ref HEAD').read().strip().replace('_','').lower()

def GetEnvVar(name, default = None):
    """Safe environment variable load that explicitly errors rather than silently failing."""

    if  'pytest' in modules:
        # if this isn't mocked, provide some dummy string
        return 'dummyenv'

    var = getenv(name)

    if  var is None:
        if  default is not None:
            return default
        raise Exception(f'Failed to load environment variable: "{name}"')
    return var
