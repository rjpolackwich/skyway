import typing_extensions as typing
import dataclasses
import json
import csv
import datetime
from dateutil.parser import parse as dateparse
import requests


class QueryBbox():
    _qname = "bbox"

    def __init__(self, bbox: typing.typing.Sequence):
        self.bbox = bbox

    def __repr__(self):
        enc = ",".join(map(str, self.bbox))
        return f'''[{self._qname}:{enc}]'''

    @property
    def bbox(self):
        return [self.south,
                self.west,
                self.north,
                self.east
                ]

    @bbox.setter
    def bbox(self, bbox):
        s, w, n, e = bbox
        self.south = s
        self.west = w
        self.north = n
        self.east = e

class QueryTimeout():
    _qname = "timeout"

    def __init__(self, timeout=360):
        self.timeout = timeout

    def __repr__(self):
        return f'''[{self._qname}:{self.timeout}]'''



class QueryPayloadFormat():
    _qname = "out"


class FormatNotImplemented(QueryPayloadFormat):
    def __init__(self, *args, **kwargs):
        raise NotImplementedError


class JSONPayload(QueryPayloadFormat):
    def __repr__(self):
        return f'''[{self._qname}:json]'''


class CSVPayload(QueryPayloadFormat):
    def __init__(self, fields=[]):
        self.fields = fields

    def __repr__(self):
        return f'''[{self._qname}:csv()]''' # fix


class XMLPayload(FormatNotImplemented): ...
class CustomPayload(FormatNotImplemented): ...
class PopupPayload(FormatNotImplemented): ...


class QueryDate():
    _qname = "date"

    def __init__(self, date: typing.typing.Union[str, datetime.datetime] = None):
        if isinstance(date, str):
            date = dateparse(date)
        assert isinstance(date, datetime.datetime)
        self.date = date

    def __repr__(self):
        return f'''[{self._qname}:"{self.date.isoformat()}"]'''


class DateDelta(QueryDate):
    _qname = "diff"

class AugmentedDateDelta(DateDelta):
    _qname = "adiff"






@dataclasses.dataclass
class QuerySettings:
    payload_format: str
    maxsize: int
    timeout: int
    datespec: typing.typing.Union[str, datetime.datetime]
    bbox: typing.typing.Sequence = dataclasses.field(default_factory=list)


    def __post_init__(self):
        pass

    def __repr__(self):
        msg = list()
        for k, v in dataclasses.asdict(self).items():
            if v is not None:
                msg.append(f'''{v}''')
        return "".join(msg) + ";"

    @classmethod
    def geom_settings(cls, date=None, bbox=None):
        return cls("json", 1073741824, 360, date, bbox)

    @classmethod
    def stats_settings(cls, date=None, bbox=None):
        return cls("csv", 536870912, 360, date, bbox)




class OSMElement(): pass

class Node(OSMElement):
    _type = "node"


class Way(OSMElement):
    _type = "way"


class Relation(OSMElement):
    _type = "relation"



