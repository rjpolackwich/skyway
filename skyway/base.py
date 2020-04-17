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


class EmptySetting():
    def __repr__(self):
        return ""



class QuerySettings():
    payload_format: str = None
    maxsize: int = None
    timeout: int = None
    datespec: typing.typing.Union[str, datetime.datetime] = None
    bbox: typing.typing.Sequence = dataclasses.field(default_factory=list)

    def __init__(self,
                 payload_format: str = None,
                 maxsize: int = None,
                 timeout: int = None,
                 datespec: typing.typing.Union[str, datetime.datetime] = None,
                 bbox: typing.typing.List = None):


    def __repr__(self):
        pass

    @property
    def payload_format(self):
        pass

    @property
    def maxsize(self):
        pass

    @property
    def timeout(self):
        pass

    @property
    def datespec(self):
        pass

    @property
    def bbox(self):
        pass





class OSMElement(): pass

class Node(OSMElement):
    _type = "node"


class Way(OSMElement):
    _type = "way"


class Relation(OSMElement):
    _type = "relation"



