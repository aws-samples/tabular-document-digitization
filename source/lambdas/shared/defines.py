# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from      pprint import pprint
from        json import loads, dumps, JSONEncoder
from      typing import List, Dict
from      dotmap import DotMap
from dataclasses import dataclass, field, fields, asdict
from     decimal import Decimal
from        uuid import uuid4
from    datetime import datetime, timedelta
from        enum import Enum

HASH = '#'

PASS = 'pass'
FAIL = 'fail'
SKIP = 'skip'

class Status:
    WAIT = 'wait'
    SKIP = 'skip'
    PASS = 'pass'
    FAIL = 'fail'
    TIME = 'time'

class Grade:
    WAIT = 'wait'
    SKIP = 'skip'
    BUSY = 'busy'
    PASS = 'pass'
    FAIL = 'fail'
    TIME = 'time'

class Stage:
    INVALID = 'invalid'
    ACQUIRE = 'acquire'
    CONVERT = 'convert'
    EXTRACT = 'extract'
    RESHAPE = 'reshape'
    OPERATE = 'operate'
    AUGMENT = 'augment'
    CATALOG = 'catalog'

class State:
    WAITING = 'waiting'
    RUNNING = 'running'
    HOLDING = 'holding'
    SUCCESS = 'success'
    FAILURE = 'failure'
    TIMEOUT = 'timeout'

class AugmentState(State):
    WAITING_PRIMARY = 'waiting-primary'
    RUNNING_PRIMARY = 'running-primary'
    WAITING_QUALITY = 'waiting-quality'
    RUNNING_QUALITY = 'running-quality'
