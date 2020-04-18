import datetime
from dateutil.parser import parse as dateparse


class QueryMetaParam():
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


class QueryPayloadFormat(QueryMetaParam, param_name="out"):
    def __init__(self, out):
        self.out = out


class QueryTimeout(QueryMetaParam, param_name="timeout"):
    def __init__(self, timeout):
        self.timeout = timeout


class QueryMaxsize(QueryMetaParam, param_name="maxsize"):
    def __init__(self, maxsize):
        self.maxsize = maxsize


class QueryBbox(QueryMetaParam, param_name="bbox"):
    def __init__(self, bbox):
        self.bbox = bbox

    def _fmt_param(self):
        return ",".join(map(str, self.bbox))


class QueryDate(QueryMetaParam, param_name="date"):
    def __init__(self, date, dqt="date"):
        self.date = date

    def _fmt_param(self):
        return self.date.isoformat()



class QuerySettings():
    def __init__(self,
                 payload_format=None,
                 timeout=None,
                 maxsize=None,
                 date=None,
                 bbox=None):

        self._out = QueryPayloadFormat(payload_format)
        self._timeout = QueryTimeout(timeout)
        self._maxsize = QueryMaxsize(maxsize)
        self._date = QueryDate(date)
        self._bbox = QueryBbox(bbox)

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
    def bbox(self):
        return self._bbox.bbox

    @bbox.setter
    def bbox(self, val):
        self._bbox.bbox = val


