import itertools

class Filter:
    def _fmt(self):
        raise NotImplementedError

    def __repr__(self):
        return self._fmt()

    def __add__(self, other):
        if isinstance(other, str):
            other = UserFilter(other)
        if isinstance(other, Filter):
            return CompoundFilter([self, other])
        if isinstance(other, CompoundFilter):
            filters = [f for f in other.filters]
            filters.append(self)
            return CompoundFilter(filters)
        else:
            raise NotImplementedError

    def __radd__(self, other):
        return self.__add__(self, other)

    def __iadd__(self, other):
        return self.__add__(other)


class CompoundFilter:
    def __init__(self, filters=[]):
        self._filters = filters

    @property
    def filters(self):
        return self._filters

    @filters.setter
    def filters(self, filters):
        if not self._filters:
            self._filters = filters
        else:
            raise AttributeError("Delete existing filters before assignment")

    @filters.deleter
    def filters(self):
        self._filters = []

    def __iter__(self):
        return iter(self.filters)

    def __repr__(self):
        return f'''{"".join(f._fmt() for f in self.filters)}'''

    def add_filter(self, other):
        if isinstance(other, str):
            other = UserFilter(other)
        if isinstance(other, Filter):
            self._filters.append(other)
            return
        if isinstance(other, CompoundFilter):
            self._filters.extend(other.filters)
            return
        else:
            raise NotImplementedError

    def __add__(self, other):
        if isinstance(other, str):
            other = UserFilter(other)
        if isinstance(other, Filter):
            filters = [f for f in self.filters]
            filters.append(other)
            return CompoundFilter(filters)
        if isinstance(other, CompoundFilter):
            filters = list(itertools.chain(self.filters, other.filters))
            return CompoundFilter(filters)
        else:
            raise NotImplementedError

    def __radd__(self, other):
        return self.__add__(other)

    def __iadd__(self, other):
        self.add_filter(other)
        return self


class UserFilter(Filter):
    def __init__(self, filterstring):
        self._fs = filterstring

    def _fmt(self):
        return self._fs


class IdFilter(Filter):
    def __init__(self, _id):
        self._id = _id

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, val):
        self._id = val

    def _fmt(self):
        return f'''(id:{self.id})'''


class BboxFilter(Filter):
    def __init__(self, bbox):
        self.bbox = bbox

    def _fmt(self):
        s, w, n, e = self.bbox
        return f'''({s:.2f},{w:.2f},{n:.2f},{e:.2f})'''


class KeySpec:
    def __init__(self, key, exists=True):
        if key.startswith("!"):
            if not exists:
                raise AttributeError("Input existence conflict")
            key = key.strip("!")
            exists = False
        self.key = key
        self.exists = exists

    def __bool__(self):
        return self.exists

    def __repr__(self):
        s = f'''{self.key}'''
        if not self.exists:
            return "!" + s
        return s



def format_values(vals):
    if isinstance(vals, str):
        return f'''={vals}'''
    if isinstance(vals, list):
        if len(vals) == 1:
            val = vals[0]
            return f'''={val}'''
        else:
            svals = "|".join(vals)
            return f'''~"^({svals})$"'''


class TagFilter(Filter):
    def __init__(self, key, vals=[], exists=True):
        if not vals:
            self._key = KeySpec(key, exists=exists)
        else:
            self._key = KeySpec(key)
        self._vals = vals
        self.exists = exists

    @property
    def key(self):
        return self._key

    @key.setter
    def key(self, val):
        self._key = KeySpec(key)

    @property
    def values(self):
        return self._vals

    @values.setter
    def values(self, vals):
        self._vals = vals

    def _fmt(self):
        if not self.key.exists:
            return f'''[{self.key}]'''
        if not self.values:
            return f'''[{self.key}]'''
        svals = format_values(self.values)
        if self.exists:
            return f'''[{self.key}{svals}]'''
        return f'''[{self.key}][{self.key}!{svals}]'''




