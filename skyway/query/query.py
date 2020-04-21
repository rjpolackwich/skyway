from .filters import BboxFilter, TagFilter, IdFilter

import datetime
from dateutil.parser import parse as dateparse


class BaseSetting:
    def __init_subclass__(cls, param_name, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._param_name = param_name

    @property
    def _alias(self):
        param = getattr(self, self.__class__._param_name)
        return param

    def __repr__(self):
        if self._alias is not None:
            return f'''[{self._param_name}:{self._fmt_param()}]'''
        return ""

    def _fmt_param(self):
        return self._alias


class PayloadFormat(BaseSetting, param_name="out"):
    def __init__(self, out):
        self.out = out


class Timeout(BaseSetting, param_name="timeout"):
    def __init__(self, timeout):
        self.timeout = timeout


class Maxsize(BaseSetting, param_name="maxsize"):
    def __init__(self, maxsize):
        self.maxsize = maxsize


class Bbox(BaseSetting, param_name="bbox"):
    def __init__(self, bbox):
        self.bbox = bbox

    def _fmt_param(self):
        s, w, n, e = self.bbox
        return f'''{s:.2f},{w:.2f},{n:.2f},{e:.2f}'''


class Date(BaseSetting, param_name="date"):
    def __init__(self, date):
        self.date = date

    def _fmt_param(self):
        return self.date.isoformat(timespec="seconds") + "Z"



class QuerySettings:
    def __init__(self,
                 payload_format=None,
                 timeout=None,
                 maxsize=None,
                 date=None,
                 bbox=None):

        self._out = PayloadFormat(payload_format)
        self._timeout = Timeout(timeout)
        self._maxsize = Maxsize(maxsize)
        self._date = Date(date)
        self._bbox = Bbox(bbox)

    def __repr__(self):
        s = (
            f'''{self._out}'''
            f'''{self._timeout}'''
            f'''{self._maxsize}'''
            f'''{self._date}'''
            f'''{self._bbox}'''
        )
        if s != "":
            s += ";"
        return s

    @property
    def payload_format(self):
        return self._out.out

    @payload_format.setter
    def payload_format(self, val):
        self._out.out = val

    @property
    def timeout(self):
        return self._timeout.timeout

    @timeout.setter
    def timeout(self, val):
        self._timeout.timeout = val

    @property
    def maxsize(self):
        return self._maxsize.maxsize

    @maxsize.setter
    def maxsize(self, val):
        self._maxsize.maxsize = val

    @property
    def date(self):
        return self._date.date

    @date.setter
    def date(self, val):
        self._date.date = val

    @property
    def bbox(self):
        return self._bbox.bbox

    @bbox.setter
    def bbox(self, val):
        self._bbox.bbox = val


class ElementType: pass


class Node(ElementType):
    def __repr__(self):
        return "node"


class Way(ElementType):
    def __repr__(self):
        return "way"


class Relation(ElementType):
    def __repr__(self):
        return "rel"


class ElementQuery: pass


class NWR(ElementType):
    def __init__(self):
        self.filters = []

    def add_tagfilter(self, tf):
        self.filters.append(tf)

    def __repr__(self):
        return f'''nwr{self.filters};'''


class QueryBuilder: pass
    overpass_endpoint = 'http://overpass-api.de/api/interpreter'


class GeomQueryBuilder(QueryBuilder):
    def __init__(self, bbox=None):
        self.settings = QuerySettings(payload_format="json", bbox=bbox)
        self.query = NWR()

    def __repr__(self):
        return f'''{self.settings}{self.query}out geom;'''

    def request(self):
        return requests.get(self.overpass_endpoint, data=repr(self))
