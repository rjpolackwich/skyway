from .filters import BboxFilter, TagFilter, IdFilter

import datetime
from dateutil.parser import parse as dateparse


class ElementQuery:
    def __init__(self, filters=None):
        self.filters = []
        self.query

    def __repr__(self):
        return f'''{self._elmtype()}{self.filters};'''


class NWR(ElementQuery):
    def __init__(self):
        self.filters = []

    def add_tagfilter(self, tf):
        self.filters.append(tf)

    def __repr__(self):
        return f'''nwr{self.filters};'''


class QueryBuilder:
    overpass_endpoint = 'http://overpass-api.de/api/interpreter'
    def __init__(self, name="default"):
        self.name = name
        self.settings = QuerySettings()
        self.queries = None




class GeomQueryBuilder(QueryBuilder):
    def __init__(self, bbox=None):
        self.settings = QuerySettings(payload_format="json", bbox=bbox)
        self.queries = NWR()

    def __repr__(self):
        return f'''{self.settings}{self.query}out geom;'''

    def request(self):
        return requests.get(self.overpass_endpoint, data=repr(self))
