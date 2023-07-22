# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from shared.defines import *
from shared.loggers import Logger
from shared.storage import S3Uri

from dataclasses import asdict, dataclass, fields, _MISSING_TYPE
from typing      import Union, Any
from json        import JSONEncoder, loads

class DocumentEncoder(JSONEncoder):
    def default(self, o):
        if  isinstance(o, Decimal):
            return int(o)
        return super(DocumentEncoder, self).default(o)

@dataclass
class StageMap:

    RetryCount: Decimal = 0
    StageS3Uri: S3Uri   = field(default_factory = S3Uri)
    ActorGrade: str     = ''
    StartStamp: str     = ''
    FinalStamp: str     = ''
    Exceptions: list    = field(default_factory = list)

    @classmethod
    def from_dict(cls, x):

        stageMap = cls()

        for field, value in x.items():
            if (field in stageMap.__dataclass_fields__ and
                stageMap.__dataclass_fields__[field].type != list and
                not isinstance(stageMap.__dataclass_fields__[field].default_factory, _MISSING_TYPE)):
                setattr(stageMap, field, stageMap.__dataclass_fields__[field].default_factory(**value))
            else:
                setattr(stageMap, field, value)

        return stageMap

# region Stage Maps

@dataclass
class AcquireMap(StageMap):
  pass

@dataclass
class ConvertMap(StageMap):
    pass
@dataclass
class ExtractMap(StageMap):
    TextractID: str = ''    # Identifier of currently running textract job.

@dataclass
class ReshapeMap(StageMap):
    pass

@dataclass
class OperateMap(StageMap):
    pass

@dataclass
class AugmentMap(StageMap):
    A2ILoopArn: str = ''
    PrimaryHLA: str = '' # Human Loop ARN for Primary A2I Workflow
    QualityHLA: str = '' # Human Loop ARN for Quality A2I Workflow

@dataclass
class CatalogMap(StageMap):
    pass

# endregion
@dataclass
class Document:
    """
    Document Abstraction Object
    """

    DocumentID: str = ''
    StageState: str = '?#?'
    OrderStamp: str = '?#?'

    AcquireMap: AcquireMap = field(default_factory = AcquireMap)
    ConvertMap: ConvertMap = field(default_factory = ConvertMap)
    ExtractMap: ExtractMap = field(default_factory = ExtractMap)
    ReshapeMap: ReshapeMap = field(default_factory = ReshapeMap)
    OperateMap: OperateMap = field(default_factory = OperateMap)
    AugmentMap: AugmentMap = field(default_factory = AugmentMap)
    CatalogMap: CatalogMap = field(default_factory = CatalogMap)

    # region Properties

    @property
    def Stage(self):
        return self.StageState.split(HASH)[0]

    @Stage.setter
    def Stage(self, x):
        _, y = self.StageState.split(HASH)
        self.StageState = f'{x}{HASH}{y}'

    @property
    def State(self):
        return self.StageState.split(HASH)[1].lower()

    @State.setter
    def State(self, y):
        x, _ = self.StageState.split(HASH)
        self.StageState = f'{x}{HASH}{y}'.title()

    @property
    def Order(self):
        return self.OrderStamp.split(HASH)[0]

    @Order.setter
    def Order(self, x):
        _, y = self.OrderStamp.split(HASH)
        self.OrderStamp = f'{x}{HASH}{y}'

    @property
    def Stamp(self):
        return self.OrderStamp.split(HASH)[1]

    @Stamp.setter
    def Stamp(self, y):
        x, _ = self.OrderStamp.split(HASH)
        self.OrderStamp = f'{x}{HASH}{y}'

    @property
    def CurrentMap(self) -> StageMap:
        return getattr(self, f'{self.Stage.title()}Map')
    
    @property
    def DocID(self):
        return self.DocumentID

    @DocID.setter
    def DocID(self, val):
        self.DocumentID = val

    @staticmethod
    def from_dict(x):
        document = Document()

        for field, value in x.items():
            if (field in document.__dataclass_fields__ and
                not isinstance(document.__dataclass_fields__[field].default_factory, _MISSING_TYPE)):
                setattr(document, field, document.__dataclass_fields__[field].default_factory.from_dict(value))
            else:
                setattr(document, field, value)

        return document

    @staticmethod
    def from_json(x):
        return Document.from_dict(loads(x))

    def to_json(self):
        return dumps(self.to_dict(), cls = DocumentEncoder)

    def to_dict(self):
        return asdict(self)


if  __name__ == '__main__':

    Logger.pretty(Document.from_dict({'DocumentID' : '123', 'AcquireMap' : {'StageS3Uri' : {'Bucket' : 'foo', 'Object' : 'bar'}, 'Exceptions' : [{'something' : 'wrong'}], 'InputS3Url' : 's3://...'}}).to_dict())

  # S3Uri(Object = 'acquire/hello.world').Put(open('sample/001.png', 'rb').read())
  # S3Uri(Object = 'acquire/hello.world').Get())

