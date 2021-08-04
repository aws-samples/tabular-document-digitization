# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from logging  import Handler, Formatter, StreamHandler, basicConfig, getLogger, getLoggerClass, setLoggerClass, DEBUG
from decimal  import Decimal
from datetime import datetime
from json     import JSONEncoder, dumps

class LoggingEncoder(JSONEncoder):
    def default(self, o):
        return (
            int(o) if isinstance(o, Decimal) else
            str(o) if isinstance(o, datetime) else
            super(LoggingEncoder, self).default(o))

class TableFormatter(Formatter):

    def format(self, record):

        time    = self.formatTime(record, '%yw%V.%w %H:%M:%S')
        level   = record.levelname
        message = record.getMessage()

        return f'{time} [{level:>8}] {message}'

class CloudLogger(getLoggerClass()):

    def __init__(self, name) -> None:
        super().__init__(name)

        streamHandler = StreamHandler()
        streamHandler.setFormatter(TableFormatter())

        self.addHandler(streamHandler)

    def pretty(self, obj, message = 'object'):

        self.info(f'{message} →\n{dumps(obj, indent = 4, cls = LoggingEncoder)}'.replace('"', "'"))

setLoggerClass(CloudLogger)

Logger = getLogger('tdd')

Logger.setLevel(DEBUG)

Logger.propagate = False

if  __name__ == '__main__':

    Logger.debug('debug')
    Logger.info('info')
    Logger.warning('warning')
    Logger.error('error')
    Logger.critical('critical')
