from .base import Filter

class GenericFilter(Filter):
    pass

class UserFilter(GenericFilter):
    def __init__(self, filterstring):
        self._fs = filterstring

    def _fmt(self):
        return self._fs


class IdFilter(GenericFilter):
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


class BboxFilter(GenericFilter):
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


class TagFilter(GenericFilter):
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




