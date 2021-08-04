# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from shared.defines import *
from shared.helpers import GetCurrentStamp

from shared.document import (
      StageMap,
    AcquireMap,
    ConvertMap,
    ExtractMap,
    ReshapeMap,
    OperateMap,
    AugmentMap,
    CatalogMap,
)

from dataclasses import asdict, dataclass, field, fields
from decimal     import Decimal
from json        import JSONEncoder, dumps
from dotmap      import DotMap

class MessageEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return int(o)
        return super(MessageEncoder, self).default(o)

@dataclass
class Message:
    """
    Generic message object.
    Serialized to SQS message body.
    """

    DocumentID: str
    ActorGrade: str      = Grade.PASS
    StartStamp: str      = field(default_factory = GetCurrentStamp)
    FinalStamp: str      = ''
  # MapUpdates: StageMap = field(default_factory = StageMap)
    MapUpdates: DotMap   = field(default_factory = DotMap)

    def to_json(self):

        return dumps(self.to_dict(), cls = MessageEncoder)

    def to_dict(self):

        d = asdict(self)

        if  type(d.get('MapUpdates', None)) == DotMap:
            d['MapUpdates'] = d['MapUpdates'].toDict()

        if  type(d.get('MapUpdates', None)) == StageMap:
            d['MapUpdates'] = d['MapUpdates'].to_dict()

        return d

    @classmethod
    def from_dict(cls, d):

        new_message = cls(**d)
        MapUpdates_field = [f for f in fields(cls) if f.name == 'MapUpdates'][0]
        new_message.MapUpdates = MapUpdates_field.default_factory(**d['MapUpdates'])

        return new_message

# Messages Sent by Respective Stage Actors for Current Map Updates

class AcquireMapUpdates(Message):
    MapUpdates: field(default_factory = AcquireMap)

class CatalogMapUpdates(Message):
    MapUpdates: field(default_factory = CatalogMap)

class ExtractMapUpdates(Message):
    MapUpdates: field(default_factory = ExtractMap)

class ReshapeMapUpdates(Message):
    MapUpdates: field(default_factory = ReshapeMap)

class OperateMapUpdates(Message):
    MapUpdates: field(default_factory = OperateMap)

class AugmentMapUpdates(Message):
    MapUpdates: field(default_factory = AugmentMap)

class ConvertMapUpdates(Message):
    MapUpdates: field(default_factory = ConvertMap)
