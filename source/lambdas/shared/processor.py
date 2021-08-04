# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from shared.defines import *
from shared.environ import *
from shared.helpers import *
from shared.loggers import Logger

from shared.database import Database
from shared.action   import Action
from shared.bus      import Bus
from shared.message  import Message

class BeginProcessor(object):
    def __init__(self, stage, actor, retryLimit, **kwArgs):

        self.stage      = stage
        self.actor      = actor
        self.retryLimit = retryLimit

        self.__dict__.update(kwArgs)

    def process(self):

        self.processDocuments()

    def processDocuments(self):

        exitLoop = 0
        outcomes = []

        for document in Database.GetDocuments(
            stages = [self.stage], states = [State.WAITING, State.HOLDING]
        ):

            status = Action.Invoke(
                function_name = self.actor,
                payload_bytes = document.to_json().encode('utf-8'),
            )

            outcomes.append(status)

            if  status == PASS:

                Logger.info(
                    f'{self.stage.title()} Begin Processor : Launching Actor for DocumentID = {document.DocumentID}, Invoke = PASS'
                )

                document.State                 = State.RUNNING
                document.CurrentMap.ActorGrade = Grade.BUSY
                document.CurrentMap.StartStamp = GetCurrentStamp()

            else:

                Logger.info(
                    f'{self.stage.title()} Begin Processor : Launching Actor for DocumentID = {document.DocumentID}, Invoke = FAIL'
                )

                document.State                  = State.HOLDING
                document.CurrentMap.ActorGrade  = Grade.WAIT
                document.CurrentMap.RetryCount += 1

                if document.CurrentMap.RetryCount > self.retryLimit:
                    document.State = State.FAILURE

                exitLoop = True

            Database.PutDocument(document)

            if  exitLoop:
                break

        Logger.info(
            f'{self.stage.title()} Begin Processor : {len(outcomes)} Documents Processed'
        )


class AwaitProcessor(object):
    def __init__(self, stage, timeoutMinutes):

        self.stage          = stage
        self.timeoutMinutes = timeoutMinutes

    def process(self):

        self.processCallbackEvents()
        self.processTimeouts()

    def processCallbackEvents(self):

        """
        Process completion events from asynchronous requests coming through the stage event bus.
        """

        for wrapper in Bus.GetMessages(stage = self.stage):

            message  = Message(**loads(wrapper.body))
            document = Database.GetDocument(document_id = message.DocumentID)

            if  not document:

                Logger.info(
                    f'{self.stage.title()} Await Processor : Received Callback for DocumentID = {message.DocumentID}, Unable to Find in Database'
                )
                wrapper.delete()
                continue

            # absorb message.MapUpdates into document
            for key, value in message.MapUpdates.items():

                Logger.info(
                    f'{self.stage.title()} Await Processor : Updating CurrentMap from Message > {key:>10} = {value}'
                )

                setattr(document.CurrentMap, key, value) # TODO Fix StageS3Uri from becoming a Dictionary

            if  message.ActorGrade == Grade.PASS:

                document.State = State.SUCCESS

                self.processCallbackEventsMore(message)

                document.CurrentMap.ActorGrade = message.ActorGrade
                document.CurrentMap.FinalStamp = GetCurrentStamp()

                Logger.info(
                    f'{self.stage.title()} Await Processor : Received Callback for DocumentID = {message.DocumentID}, Status is PASS'
                )

            else:

                document.State                 = State.FAILURE
                document.CurrentMap.ActorGrade = message.ActorGrade
                document.CurrentMap.FinalStamp = GetCurrentStamp()

                self.processCallbackEventsMore(message)

                Logger.info(
                    f'{self.stage.title()} Await Processor : Received Callback for DocumentID = {message.DocumentID}, Status is FAIL'
                )

            Database.PutDocument(document)

            wrapper.delete()

    def processCallbackEventsMore(self, message):
        pass

    def processTimeouts(self):
        """
        Ascertain errant asynchronous requests which have not yet completed by a pre-specified time limit.
        """

        def isOverTime(begin_stamp, minutes):

            return datetime.now() > datetime.fromisoformat(begin_stamp) + timedelta(minutes = minutes)

        for document in Database.GetDocuments(
            stages = [self.stage], states = [State.RUNNING]
        ):

            if  isOverTime(document.CurrentMap.StartStamp, minutes = self.timeoutMinutes):

                document.State                 = State.TIMEOUT
                document.CurrentMap.ActorGrade = Grade.TIME
                document.CurrentMap.FinalStamp = GetCurrentStamp()

                Logger.info(
                    f'{self.stage.title()} Await Processor : Detected Time-Out for DocumentID = {document.DocumentID}'
                )

                Database.PutDocument(document)


class ActorProcessor(object):

    pass